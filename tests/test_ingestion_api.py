from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.app import _signature, create_app

DEVICE_SECRET = "test-device-secret-not-for-production"
READ_TOKEN = "test-read-token-not-for-production"


def make_client(tmp_path):
    app = create_app(
        db_path=str(tmp_path / "readings.sqlite3"),
        device_secret=DEVICE_SECRET,
        read_token=READ_TOKEN,
    )
    return TestClient(app)


def signed_headers(body: bytes, nonce: str = "nonce-123456789012345") -> dict[str, str]:
    timestamp = str(int(time.time()))
    return {
        "content-type": "application/json",
        "x-device-timestamp": timestamp,
        "x-device-nonce": nonce,
        "x-device-signature": _signature(DEVICE_SECRET, timestamp, nonce, body),
    }


def valid_body() -> bytes:
    return json.dumps(
        {
            "device_id": "esp32-lab-01",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": 36.7,
            "bpm": 78,
        },
        separators=(",", ":"),
    ).encode()


def test_signed_reading_is_stored_and_requires_separate_read_token(tmp_path):
    client = make_client(tmp_path)
    body = valid_body()
    response = client.post(
        "/api/v1/readings",
        content=body,
        headers=signed_headers(body, "nonce-valid-00000001"),
    )
    assert response.status_code == 201
    assert response.json()["status"] == "accepted"

    assert client.get("/api/v1/readings").status_code == 401
    result = client.get(
        "/api/v1/readings",
        headers={"Authorization": f"Bearer {READ_TOKEN}"},
    )
    assert result.status_code == 200
    reading = result.json()["readings"][0]
    assert reading["device_id"] == "esp32-lab-01"
    assert reading["bpm"] == 78


def test_invalid_signature_is_rejected(tmp_path):
    client = make_client(tmp_path)
    body = valid_body()
    headers = signed_headers(body, "nonce-invalid-00000001")
    headers["x-device-signature"] = "0" * 64
    assert client.post("/api/v1/readings", content=body, headers=headers).status_code == 401


def test_nonce_cannot_be_replayed(tmp_path):
    client = make_client(tmp_path)
    body = valid_body()
    headers = signed_headers(body, "nonce-replay-000000001")
    assert client.post("/api/v1/readings", content=body, headers=headers).status_code == 201
    assert client.post("/api/v1/readings", content=body, headers=headers).status_code == 409


def test_out_of_range_sensor_reading_is_rejected(tmp_path):
    client = make_client(tmp_path)
    body = json.dumps(
        {
            "device_id": "esp32-lab-01",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": 999,
            "bpm": 78,
        },
        separators=(",", ":"),
    ).encode()
    response = client.post(
        "/api/v1/readings",
        content=body,
        headers=signed_headers(body, "nonce-range-000000001"),
    )
    assert response.status_code == 422


def test_stale_device_request_is_rejected(tmp_path):
    client = make_client(tmp_path)
    body = valid_body()
    headers = signed_headers(body, "nonce-stale-000000001")
    headers["x-device-timestamp"] = str(int(time.time()) - 3600)
    headers["x-device-signature"] = _signature(
        DEVICE_SECRET, headers["x-device-timestamp"], headers["x-device-nonce"], body
    )
    assert client.post("/api/v1/readings", content=body, headers=headers).status_code == 401


def test_health_endpoint_does_not_require_credentials(tmp_path):
    client = make_client(tmp_path)
    assert client.get("/healthz").json() == {"status": "ok"}
