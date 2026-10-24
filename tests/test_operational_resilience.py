from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app import _signature, create_app
from backend.maintenance import backup_database, prune_database, retention_counts
from simulator.device_simulator import send_reading_with_retry

DEVICE_SECRET = "device-secret-for-tests-only"
READ_TOKEN = "read-token-for-tests-only"
SESSION_SECRET = "session-secret-for-tests-only-longer-than-32-characters"


def signed_request(device_id: str, nonce: str = "operational-test-nonce-0001"):
    body = json.dumps(
        {
            "device_id": device_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": 36.5,
            "bpm": 72,
        },
        separators=(",", ":"),
    ).encode()
    timestamp = str(int(time.time()))
    return body, {
        "Content-Type": "application/json",
        "X-Device-Timestamp": timestamp,
        "X-Device-Nonce": nonce,
        "X-Device-Signature": _signature(DEVICE_SECRET, timestamp, nonce, body),
    }


def test_per_device_key_enrollment_and_unknown_device_rejection(tmp_path):
    client = TestClient(
        create_app(
            db_path=str(tmp_path / "readings.sqlite3"),
            device_secrets={"esp32-a": DEVICE_SECRET},
            read_token=READ_TOKEN,
        )
    )
    body, headers = signed_request("esp32-a")
    assert client.post("/api/v1/readings", content=body, headers=headers).status_code == 201

    unknown_body, unknown_headers = signed_request("esp32-unknown", "operational-test-nonce-0002")
    response = client.post("/api/v1/readings", content=unknown_body, headers=unknown_headers)
    assert response.status_code == 401
    assert "enrolled" not in response.text.lower()


def test_login_rate_limit_and_audit_endpoint(tmp_path, monkeypatch):
    monkeypatch.setenv("IOT_MAINTENANCE_TOKEN", "maintenance-token-for-tests")
    client = TestClient(
        create_app(
            db_path=str(tmp_path / "readings.sqlite3"),
            dashboard_password="dashboard-password",
            session_secret=SESSION_SECRET,
            dashboard_origin="http://testserver",
            secure_cookies=False,
            login_rate_limit=2,
            rate_window_seconds=60,
        )
    )
    for _ in range(2):
        response = client.post(
            "/api/v1/dashboard/login",
            json={"password": "wrong-password"},
            headers={"Origin": "http://testserver"},
        )
        assert response.status_code == 401
    limited = client.post(
        "/api/v1/dashboard/login",
        json={"password": "wrong-password"},
        headers={"Origin": "http://testserver"},
    )
    assert limited.status_code == 429
    assert limited.headers["retry-after"] == "60"

    assert client.get("/api/v1/admin/audit").status_code == 401
    audit = client.get(
        "/api/v1/admin/audit",
        headers={"Authorization": "Bearer maintenance-token-for-tests"},
    )
    assert audit.status_code == 200
    assert [event["event_type"] for event in audit.json()["events"]].count("dashboard_login_failed") == 2
    assert all("password" not in json.dumps(event).lower() for event in audit.json()["events"])


def test_readiness_endpoint_checks_database(tmp_path):
    client = TestClient(create_app(db_path=str(tmp_path / "readings.sqlite3")))
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").json() == {"status": "ready"}


def test_simulator_retry_uses_bounded_exponential_backoff():
    statuses = iter([503, 429, 201])
    delays = []
    calls = []

    def sender(url, secret, reading):
        calls.append((url, secret, reading))
        return next(statuses)

    status = send_reading_with_retry(
        "https://api.example.invalid/api/v1/readings",
        DEVICE_SECRET,
        {"device_id": "esp32-a"},
        attempts=3,
        base_delay=0.5,
        sleeper=delays.append,
        sender=sender,
    )
    assert status == 201
    assert len(calls) == 3
    assert delays == [0.5, 1.0]


def test_simulator_does_not_retry_permanent_client_errors():
    calls = []

    def sender(url, secret, reading):
        calls.append(1)
        return 422

    assert send_reading_with_retry(
        "https://api.example.invalid/api/v1/readings",
        DEVICE_SECRET,
        {"device_id": "esp32-a"},
        sleeper=lambda _: None,
        sender=sender,
    ) == 422
    assert len(calls) == 1


def test_retention_requires_backup_and_removes_only_expired_records(tmp_path):
    database = tmp_path / "readings.sqlite3"
    from backend.app import _connect

    old = (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()
    fresh = datetime.now(timezone.utc).isoformat()
    with _connect(str(database)) as connection:
        connection.execute(
            "INSERT INTO readings(device_id, timestamp, temperature, bpm, received_at) VALUES (?, ?, ?, ?, ?)",
            ("esp32-old", old, 36.5, 72, old),
        )
        connection.execute(
            "INSERT INTO readings(device_id, timestamp, temperature, bpm, received_at) VALUES (?, ?, ?, ?, ?)",
            ("esp32-new", fresh, 36.5, 72, fresh),
        )
        connection.execute(
            "INSERT INTO audit_events(event_type, actor_id, occurred_at) VALUES (?, ?, ?)",
            ("reading_accepted", "esp32-old", old),
        )

    counts = retention_counts(str(database), 90)
    assert counts["readings"] == 1
    assert counts["audit_events"] == 1

    backup = backup_database(str(database), str(tmp_path / "backups" / "pre-purge.sqlite3"))
    assert backup.exists()
    assert retention_counts(str(backup), 90)["readings"] == 1

    deleted = prune_database(str(database), 90)
    assert deleted["readings"] == 1
    assert deleted["audit_events"] == 1
    assert retention_counts(str(database), 90)["readings"] == 0


def test_backup_refuses_to_overwrite_or_replace_source(tmp_path):
    database = tmp_path / "readings.sqlite3"
    from backend.app import _connect

    with _connect(str(database)):
        pass
    try:
        backup_database(str(database), str(database))
    except ValueError:
        pass
    else:
        raise AssertionError("backup must not replace the source database")

    target = tmp_path / "backup.sqlite3"
    backup_database(str(database), str(target))
    try:
        backup_database(str(database), str(target))
    except FileExistsError:
        pass
    else:
        raise AssertionError("backup must not overwrite an existing backup")
