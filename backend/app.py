"""Authenticated sensor-ingestion API and session-protected dashboard."""
from __future__ import annotations

import hashlib
import hmac
import json
from collections import defaultdict, deque
import os
import re
import secrets
import sqlite3
import time
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

MAX_BODY_BYTES = 16 * 1024
MAX_LOGIN_BODY_BYTES = 2 * 1024
SIGNATURE_WINDOW_SECONDS = 300
DASHBOARD_SESSION_SECONDS = 1800
NONCE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
DEVICE_ID_PATTERN = r"^[A-Za-z0-9_-]+$"
SESSION_COOKIE_NAME = "iot_dashboard_session"
ROOT = Path(__file__).resolve().parent.parent
RATE_WINDOW_SECONDS = 60
LOGIN_RATE_LIMIT = 5
INGEST_RATE_LIMIT = 120


class Reading(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    device_id: str = Field(min_length=1, max_length=64, pattern=DEVICE_ID_PATTERN)
    timestamp: datetime
    temperature: float = Field(ge=-20, le=80, allow_inf_nan=False)
    bpm: int = Field(ge=20, le=250)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _connect(db_path: str) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            temperature REAL NOT NULL,
            bpm INTEGER NOT NULL,
            received_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS used_nonces (
            nonce TEXT PRIMARY KEY,
            seen_at INTEGER NOT NULL
        )
        """
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings(timestamp)"
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_readings_device_timestamp ON readings(device_id, timestamp)"
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            actor_id TEXT NOT NULL,
            occurred_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_audit_events_occurred_at ON audit_events(occurred_at)"
    )
    return connection


def _record_audit(db_path: str, event_type: str, actor_id: str) -> None:
    """Store security-relevant metadata only; never record credentials or reading values."""
    try:
        with closing(_connect(db_path)) as connection, connection:
            connection.execute(
                "INSERT INTO audit_events(event_type, actor_id, occurred_at) VALUES (?, ?, ?)",
                (event_type, actor_id[:64], _utc_now().isoformat()),
            )
    except sqlite3.Error:
        # Auditing must not turn a valid request into an outage; deployments should monitor storage.
        return


def _signature(secret: str, timestamp: str, nonce: str, body: bytes) -> str:
    message = timestamp.encode("ascii") + b"." + nonce.encode("ascii") + b"." + body
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def _normalize_filter_timestamp(value: datetime | None, label: str) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None or value.utcoffset() is None:
        raise HTTPException(status_code=422, detail=f"{label} must include a timezone")
    return value.astimezone(timezone.utc).isoformat()


async def _read_limited_body(request: Request, maximum: int) -> bytes:
    """Read a request incrementally so chunked bodies cannot bypass size limits."""
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > maximum:
        raise HTTPException(status_code=413, detail="Request body too large")
    chunks: list[bytes] = []
    total = 0
    async for chunk in request.stream():
        total += len(chunk)
        if total > maximum:
            raise HTTPException(status_code=413, detail="Request body too large")
        chunks.append(chunk)
    return b"".join(chunks)


def _make_session(secret: str, now: int | None = None) -> str:
    expires = (now if now is not None else int(time.time())) + DASHBOARD_SESSION_SECONDS
    nonce = secrets.token_urlsafe(24)
    payload = f"{expires}.{nonce}"
    signature = hmac.new(secret.encode("utf-8"), payload.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def _valid_session(value: str | None, secret: str, now: int | None = None) -> bool:
    if not value:
        return False
    try:
        expires_text, nonce, supplied_signature = value.split(".", 2)
        if not expires_text.isascii() or not expires_text.isdigit() or not nonce:
            return False
        expires = int(expires_text)
        current = now if now is not None else int(time.time())
        if expires <= current or expires > current + DASHBOARD_SESSION_SECONDS:
            return False
        payload = f"{expires_text}.{nonce}"
        expected = hmac.new(secret.encode("utf-8"), payload.encode("ascii"), hashlib.sha256).hexdigest()
        return secrets.compare_digest(expected, supplied_signature)
    except (ValueError, UnicodeEncodeError):
        return False


def create_app(
    db_path: str | None = None,
    device_secret: str | None = None,
    read_token: str | None = None,
    dashboard_password: str | None = None,
    session_secret: str | None = None,
    dashboard_origin: str | None = None,
    secure_cookies: bool | None = None,
    device_secrets: dict[str, str] | None = None,
    login_rate_limit: int = LOGIN_RATE_LIMIT,
    ingest_rate_limit: int = INGEST_RATE_LIMIT,
    rate_window_seconds: int = RATE_WINDOW_SECONDS,
) -> FastAPI:
    """Build the app; injectable settings make isolated tests deterministic."""
    database = db_path or os.getenv("IOT_DATABASE_PATH", "data/readings.sqlite3")
    configured_dashboard_password = dashboard_password or os.getenv("IOT_DASHBOARD_PASSWORD")
    configured_session_secret = session_secret or os.getenv("IOT_SESSION_SECRET")
    raw_device_secrets = os.getenv("IOT_DEVICE_SECRETS_JSON")
    if device_secrets is None and raw_device_secrets:
        try:
            parsed_device_secrets = json.loads(raw_device_secrets)
            if not isinstance(parsed_device_secrets, dict) or not all(
                isinstance(key, str) and isinstance(value, str) and value
                for key, value in parsed_device_secrets.items()
            ):
                raise ValueError("IOT_DEVICE_SECRETS_JSON must map device IDs to non-empty secrets")
            device_secrets = parsed_device_secrets
        except (json.JSONDecodeError, ValueError) as error:
            raise ValueError("Invalid IOT_DEVICE_SECRETS_JSON configuration") from error
    configured_device_secrets = device_secrets
    allowed_origin = (dashboard_origin or os.getenv("IOT_DASHBOARD_ORIGIN") or "http://127.0.0.1:8000").rstrip("/")
    if secure_cookies is None:
        secure_cookies = os.getenv("IOT_COOKIE_SECURE", "true").strip().lower() not in {"0", "false", "no"}

    app = FastAPI(
        title="ESP32 Health Monitoring Ingestion API",
        version="1.2.0",
        description="Authenticated ingestion, history access, and a session-protected dashboard.",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    rate_buckets: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    @app.middleware("http")
    async def apply_local_rate_limits(request: Request, call_next):
        path = request.url.path
        if request.method == "POST" and path in {"/api/v1/dashboard/login", "/api/v1/readings"}:
            limit = login_rate_limit if path.endswith("/login") else ingest_rate_limit
            host = request.client.host if request.client else "unknown"
            bucket_key = (path, host)
            now = time.monotonic()
            bucket = rate_buckets[bucket_key]
            while bucket and bucket[0] <= now - rate_window_seconds:
                bucket.popleft()
            if len(bucket) >= limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"},
                    headers={"Retry-After": str(max(1, rate_window_seconds))},
                )
            bucket.append(now)
        return await call_next(request)

    def require_dashboard_session(request: Request) -> None:
        if not configured_session_secret or len(configured_session_secret) < 32:
            raise HTTPException(status_code=503, detail="Dashboard sessions are not configured")
        cookie = request.cookies.get(SESSION_COOKIE_NAME)
        if not _valid_session(cookie, configured_session_secret):
            raise HTTPException(status_code=401, detail="Dashboard login required")

    def require_same_origin(request: Request) -> None:
        origin = request.headers.get("origin", "").rstrip("/")
        if not origin or not secrets.compare_digest(origin.encode("utf-8"), allowed_origin.encode("utf-8")):
            raise HTTPException(status_code=403, detail="Cross-origin request rejected")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz() -> dict[str, str]:
        try:
            with closing(_connect(database)) as connection:
                connection.execute("SELECT 1").fetchone()
        except sqlite3.Error:
            raise HTTPException(status_code=503, detail="Storage unavailable") from None
        return {"status": "ready"}

    @app.get("/dashboard", include_in_schema=False)
    def dashboard_page() -> Response:
        return FileResponse(
            ROOT / "health" / "api_dashboard.html",
            media_type="text/html",
            headers={
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
                "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
            },
        )

    @app.get("/dashboard.js", include_in_schema=False)
    def dashboard_script() -> Response:
        return FileResponse(
            ROOT / "health" / "api_dashboard.js",
            media_type="text/javascript",
            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
        )

    @app.post("/api/v1/dashboard/login")
    async def dashboard_login(request: Request, response: Response) -> dict[str, str]:
        require_same_origin(request)
        if not configured_dashboard_password:
            raise HTTPException(status_code=503, detail="Dashboard login is not configured")
        if not configured_session_secret or len(configured_session_secret) < 32:
            raise HTTPException(status_code=503, detail="Dashboard sessions are not configured")

        body = await _read_limited_body(request, MAX_LOGIN_BODY_BYTES)
        try:
            credentials = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise HTTPException(status_code=400, detail="Invalid login request") from None
        password = credentials.get("password") if isinstance(credentials, dict) else None
        if not isinstance(password, str) or not secrets.compare_digest(
            configured_dashboard_password.encode("utf-8"), password.encode("utf-8")
        ):
            _record_audit(database, "dashboard_login_failed", "dashboard")
            raise HTTPException(status_code=401, detail="Invalid dashboard credentials")

        _record_audit(database, "dashboard_login_succeeded", "dashboard")
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=_make_session(configured_session_secret),
            max_age=DASHBOARD_SESSION_SECONDS,
            httponly=True,
            secure=secure_cookies,
            samesite="strict",
            path="/",
        )
        response.headers["Cache-Control"] = "no-store"
        return {"status": "authenticated"}

    @app.post("/api/v1/dashboard/logout")
    def dashboard_logout(request: Request, response: Response) -> dict[str, str]:
        require_same_origin(request)
        require_dashboard_session(request)
        _record_audit(database, "dashboard_logout", "dashboard")
        response.delete_cookie(
            key=SESSION_COOKIE_NAME,
            path="/",
            httponly=True,
            secure=secure_cookies,
            samesite="strict",
        )
        response.headers["Cache-Control"] = "no-store"
        return {"status": "logged_out"}

    @app.get("/api/v1/dashboard/readings")
    def dashboard_readings(
        request: Request,
        response: Response,
        limit: int = Query(default=100, ge=1, le=500),
        device_id: str | None = Query(default=None, min_length=1, max_length=64, pattern=DEVICE_ID_PATTERN),
    ) -> dict[str, object]:
        require_dashboard_session(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        try:
            with _connect(database) as connection:
                rows = connection.execute(
                    """
                    SELECT id, device_id, timestamp, temperature, bpm, received_at
                    FROM readings
                    WHERE (? IS NULL OR device_id = ?)
                    ORDER BY timestamp DESC, id DESC
                    LIMIT ?
                    """,
                    (device_id, device_id, limit),
                ).fetchall()
        except sqlite3.Error:
            raise HTTPException(status_code=503, detail="Storage temporarily unavailable") from None
        return {"readings": [dict(row) for row in rows], "count": len(rows), "limit": limit}

    @app.post("/api/v1/readings", status_code=201)
    async def ingest_reading(
        request: Request,
        x_device_timestamp: Annotated[str | None, Header()] = None,
        x_device_nonce: Annotated[str | None, Header()] = None,
        x_device_signature: Annotated[str | None, Header()] = None,
    ) -> dict[str, object]:
        legacy_secret = device_secret or os.getenv("IOT_DEVICE_HMAC_SECRET")
        if not configured_device_secrets and not legacy_secret:
            raise HTTPException(status_code=503, detail="Device ingestion is not configured")
        if not x_device_timestamp or not x_device_nonce or not x_device_signature:
            raise HTTPException(status_code=401, detail="Missing device authentication headers")
        if (
            not x_device_timestamp.isascii()
            or not x_device_timestamp.isdigit()
            or len(x_device_timestamp) > 12
        ):
            raise HTTPException(status_code=401, detail="Invalid device authentication")
        if not NONCE_PATTERN.fullmatch(x_device_nonce):
            raise HTTPException(status_code=401, detail="Invalid device authentication")

        now = int(time.time())
        sent_at = int(x_device_timestamp)
        if abs(now - sent_at) > SIGNATURE_WINDOW_SECONDS:
            raise HTTPException(status_code=401, detail="Expired device request")

        body = await _read_limited_body(request, MAX_BODY_BYTES)

        try:
            reading = Reading.model_validate_json(body)
        except (ValidationError, UnicodeDecodeError, TypeError):
            raise HTTPException(status_code=422, detail="Invalid reading payload") from None

        secret = (
            configured_device_secrets.get(reading.device_id)
            if configured_device_secrets is not None
            else legacy_secret
        )
        if not secret:
            # Do not disclose whether a device ID has been enrolled.
            raise HTTPException(status_code=401, detail="Invalid device authentication")
        expected = _signature(secret, x_device_timestamp, x_device_nonce, body)
        if not re.fullmatch(r"[0-9a-fA-F]{64}", x_device_signature) or not hmac.compare_digest(
            expected, x_device_signature.lower()
        ):
            raise HTTPException(status_code=401, detail="Invalid device authentication")

        timestamp = reading.timestamp
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise HTTPException(status_code=422, detail="timestamp must include a timezone")
        normalized_timestamp = timestamp.astimezone(timezone.utc).isoformat()
        try:
            with closing(_connect(database)) as connection, connection:
                connection.execute(
                    "DELETE FROM used_nonces WHERE seen_at < ?",
                    (now - SIGNATURE_WINDOW_SECONDS * 2,),
                )
                connection.execute(
                    "INSERT INTO used_nonces(nonce, seen_at) VALUES (?, ?)",
                    (x_device_nonce, now),
                )
                cursor = connection.execute(
                    """
                    INSERT INTO readings(device_id, timestamp, temperature, bpm, received_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        reading.device_id,
                        normalized_timestamp,
                        reading.temperature,
                        reading.bpm,
                        _utc_now().isoformat(),
                    ),
                )
                reading_id = cursor.lastrowid
                connection.execute(
                    "INSERT INTO audit_events(event_type, actor_id, occurred_at) VALUES (?, ?, ?)",
                    ("reading_accepted", reading.device_id, _utc_now().isoformat()),
                )
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Device request already used") from None
        except sqlite3.Error:
            raise HTTPException(status_code=503, detail="Storage temporarily unavailable") from None
        return {"id": reading_id, "status": "accepted"}

    @app.get("/api/v1/admin/audit")
    def list_audit_events(
        authorization: Annotated[str | None, Header()] = None,
        limit: int = Query(default=100, ge=1, le=500),
    ) -> dict[str, object]:
        expected_token = os.getenv("IOT_MAINTENANCE_TOKEN", "")
        scheme, separator, supplied_token = (authorization or "").partition(" ")
        if not expected_token:
            raise HTTPException(status_code=503, detail="Maintenance access is not configured")
        if not separator or scheme.lower() != "bearer" or not secrets.compare_digest(
            expected_token.encode("utf-8"), supplied_token.encode("utf-8")
        ):
            raise HTTPException(status_code=401, detail="Maintenance authentication required")
        try:
            with closing(_connect(database)) as connection:
                rows = connection.execute(
                    "SELECT id, event_type, actor_id, occurred_at FROM audit_events ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        except sqlite3.Error:
            raise HTTPException(status_code=503, detail="Storage temporarily unavailable") from None
        return {"events": [dict(row) for row in rows], "count": len(rows), "limit": limit}

    @app.get("/api/v1/readings")
    def list_readings(
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
        limit: int = Query(default=100, ge=1, le=500),
        device_id: str | None = Query(default=None, min_length=1, max_length=64, pattern=DEVICE_ID_PATTERN),
        start: datetime | None = Query(default=None),
        end: datetime | None = Query(default=None),
    ) -> dict[str, object]:
        expected_token = read_token or os.getenv("IOT_READ_API_TOKEN")
        scheme, separator, supplied_token = (authorization or "").partition(" ")
        if (
            not expected_token
            or not separator
            or scheme.lower() != "bearer"
            or not supplied_token
            or not secrets.compare_digest(expected_token.encode("utf-8"), supplied_token.encode("utf-8"))
        ):
            if not expected_token:
                raise HTTPException(status_code=503, detail="Reading access is not configured")
            raise HTTPException(status_code=401, detail="Reading access requires authentication")

        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        start_utc = _normalize_filter_timestamp(start, "start")
        end_utc = _normalize_filter_timestamp(end, "end")
        if start_utc and end_utc and start_utc > end_utc:
            raise HTTPException(status_code=422, detail="start must be earlier than or equal to end")
        parameters: list[object] = [
            device_id, device_id, start_utc, start_utc, end_utc, end_utc, limit,
        ]
        try:
            with _connect(database) as connection:
                rows = connection.execute(
                    """
                    SELECT id, device_id, timestamp, temperature, bpm, received_at
                    FROM readings
                    WHERE (? IS NULL OR device_id = ?)
                      AND (? IS NULL OR timestamp >= ?)
                      AND (? IS NULL OR timestamp <= ?)
                    ORDER BY timestamp DESC, id DESC
                    LIMIT ?
                    """,
                    parameters,
                ).fetchall()
        except sqlite3.Error:
            raise HTTPException(status_code=503, detail="Storage temporarily unavailable") from None
        return {
            "readings": [dict(row) for row in rows],
            "count": len(rows),
            "limit": limit,
            "filters": {"device_id": device_id, "start": start_utc, "end": end_utc},
        }

    return app


app = create_app()
