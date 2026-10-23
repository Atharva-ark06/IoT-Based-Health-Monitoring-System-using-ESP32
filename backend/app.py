"""Authenticated sensor-ingestion API for the ESP32 health-monitoring demo.

Run behind an HTTPS reverse proxy. This service deliberately does not enable CORS
or expose credentials to the browser dashboard.
"""
from __future__ import annotations

import hashlib
from contextlib import closing
import hmac
import os
import re
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, ValidationError

MAX_BODY_BYTES = 16 * 1024
SIGNATURE_WINDOW_SECONDS = 300
NONCE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{16,128}$")


class Reading(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    device_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
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
    return connection


def _signature(secret: str, timestamp: str, nonce: str, body: bytes) -> str:
    message = timestamp.encode("ascii") + b"." + nonce.encode("ascii") + b"." + body
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def create_app(
    db_path: str | None = None,
    device_secret: str | None = None,
    read_token: str | None = None,
) -> FastAPI:
    """Build the app; optional parameters make isolated tests deterministic."""
    database = db_path or os.getenv("IOT_DATABASE_PATH", "data/readings.sqlite3")
    app = FastAPI(
        title="ESP32 Health Monitoring Ingestion API",
        version="1.0.0",
        description="Authenticated ingestion and separately authenticated reading access.",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/v1/readings", status_code=201)
    async def ingest_reading(
        request: Request,
        x_device_timestamp: Annotated[str | None, Header()] = None,
        x_device_nonce: Annotated[str | None, Header()] = None,
        x_device_signature: Annotated[str | None, Header()] = None,
    ) -> dict[str, object]:
        secret = device_secret or os.getenv("IOT_DEVICE_HMAC_SECRET")
        if not secret:
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

        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > MAX_BODY_BYTES:
            raise HTTPException(status_code=413, detail="Request body too large")

        body = await request.body()
        if len(body) > MAX_BODY_BYTES:
            raise HTTPException(status_code=413, detail="Request body too large")

        expected = _signature(secret, x_device_timestamp, x_device_nonce, body)
        if not hmac.compare_digest(expected, x_device_signature.lower()):
            raise HTTPException(status_code=401, detail="Invalid device authentication")

        try:
            reading = Reading.model_validate_json(body)
        except (ValidationError, UnicodeDecodeError, TypeError):
            raise HTTPException(status_code=422, detail="Invalid reading payload") from None

        # Normalize timestamps to UTC so comparisons and retention are consistent.
        timestamp = reading.timestamp
        if timestamp.tzinfo is None:
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
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Device request already used") from None
        except sqlite3.Error:
            # Avoid returning database paths, SQL, or payload details to callers.
            raise HTTPException(status_code=503, detail="Storage temporarily unavailable") from None

        return {"id": reading_id, "status": "accepted"}

    @app.get("/api/v1/readings")
    def list_readings(
        authorization: Annotated[str | None, Header()] = None,
        limit: int = Query(default=100, ge=1, le=500),
    ) -> dict[str, object]:
        expected_token = read_token or os.getenv("IOT_READ_API_TOKEN")
        if not expected_token:
            raise HTTPException(status_code=503, detail="Reading access is not configured")
        scheme, separator, supplied_token = (authorization or "").partition(" ")
        if (
            not separator
            or scheme.lower() != "bearer"
            or not supplied_token
            or not secrets.compare_digest(expected_token, supplied_token)
        ):
            raise HTTPException(status_code=401, detail="Reading access requires authentication")

        try:
            with _connect(database) as connection:
                rows = connection.execute(
                    """
                    SELECT id, device_id, timestamp, temperature, bpm, received_at
                    FROM readings ORDER BY id DESC LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
        except sqlite3.Error:
            raise HTTPException(status_code=503, detail="Storage temporarily unavailable") from None

        return {"readings": [dict(row) for row in rows]}

    return app


app = create_app()
