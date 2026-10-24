from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.app import MAX_BODY_BYTES, _signature, create_app

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


def valid_body(**overrides) -> bytes:
    reading = {
        "device_id": "esp32-lab-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": 36.7,
        "bpm": 78,
    }
    reading.update(overrides)
    return json.dumps(reading, separators=(",", ":")).encode()


def post_signed(client, body: bytes, nonce: str) :
    return client.post(
        "/api/v1/readings",
        content=body,
        headers=signed_headers(body, nonce),
    )


def read_headers(token: str = READ_TOKEN) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_signed_reading_is_stored_and_requires_separate_read_token(tmp_path):
    client = make_client(tmp_path)
    body = valid_body()
    response = post_signed(client, body, "nonce-valid-00000001")
    assert response.status_code == 201
    assert response.json()["status"] == "accepted"

    assert client.get("/api/v1/readings").status_code == 401
    result = client.get("/api/v1/readings", headers=read_headers())
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


def test_missing_device_authentication_headers_are_rejected(tmp_path):
    client = make_client(tmp_path)
    assert client.post("/api/v1/readings", content=valid_body()).status_code == 401


def test_malformed_device_timestamp_header_is_rejected(tmp_path):
    client = make_client(tmp_path)
    body = valid_body()
    headers = signed_headers(body, "nonce-bad-time-00000001")
    headers["x-device-timestamp"] = "not-a-timestamp"
    assert client.post("/api/v1/readings", content=body, headers=headers).status_code == 401


def test_nonce_cannot_be_replayed(tmp_path):
    client = make_client(tmp_path)
    body = valid_body()
    headers = signed_headers(body, "nonce-replay-000000001")
    assert client.post("/api/v1/readings", content=body, headers=headers).status_code == 201
    assert client.post("/api/v1/readings", content=body, headers=headers).status_code == 409


def test_out_of_range_sensor_reading_is_rejected(tmp_path):
    client = make_client(tmp_path)
    body = valid_body(temperature=999)
    response = post_signed(client, body, "nonce-range-000000001")
    assert response.status_code == 422


def test_unexpected_payload_fields_are_rejected(tmp_path):
    client = make_client(tmp_path)
    body = valid_body(unexpected="not-allowed")
    assert post_signed(client, body, "nonce-extra-000000001").status_code == 422


def test_timezone_naive_sensor_timestamp_is_rejected(tmp_path):
    client = make_client(tmp_path)
    body = valid_body(timestamp="2026-10-22T10:00:00")
    assert post_signed(client, body, "nonce-naive-000000001").status_code == 422


def test_oversized_body_is_rejected_before_signature_validation(tmp_path):
    client = make_client(tmp_path)
    body = b" " * (MAX_BODY_BYTES + 1)
    headers = signed_headers(b"{}", "nonce-large-000000001")
    headers["content-length"] = str(len(body))
    assert client.post("/api/v1/readings", content=body, headers=headers).status_code == 413


def test_chunked_oversized_body_is_rejected_without_content_length(tmp_path):
    client = make_client(tmp_path)

    def chunks():
        yield b" " * (MAX_BODY_BYTES // 2)
        yield b" " * (MAX_BODY_BYTES // 2 + 1)

    headers = signed_headers(b"{}", "nonce-chunked-large-0001")
    response = client.post("/api/v1/readings", content=chunks(), headers=headers)
    assert response.status_code == 413


def test_stale_device_request_is_rejected(tmp_path):
    client = make_client(tmp_path)
    body = valid_body()
    headers = signed_headers(body, "nonce-stale-000000001")
    headers["x-device-timestamp"] = str(int(time.time()) - 3600)
    headers["x-device-signature"] = _signature(
        DEVICE_SECRET, headers["x-device-timestamp"], headers["x-device-nonce"], body
    )
    assert client.post("/api/v1/readings", content=body, headers=headers).status_code == 401


def test_read_endpoint_rejects_invalid_token(tmp_path):
    client = make_client(tmp_path)
    response = client.get("/api/v1/readings", headers=read_headers("wrong-token"))
    assert response.status_code == 401


def test_history_can_be_filtered_by_device_and_time(tmp_path):
    client = make_client(tmp_path)
    first = valid_body(
        device_id="esp32-lab-01",
        timestamp="2026-10-22T10:00:00+00:00",
        temperature=36.5,
        bpm=72,
    )
    second = valid_body(
        device_id="esp32-lab-02",
        timestamp="2026-10-22T11:00:00+00:00",
        temperature=37.0,
        bpm=88,
    )
    assert post_signed(client, first, "nonce-history-00000001").status_code == 201
    assert post_signed(client, second, "nonce-history-00000002").status_code == 201

    response = client.get(
        "/api/v1/readings?device_id=esp32-lab-01&start=2026-10-22T09:00:00Z&end=2026-10-22T10:30:00Z",
        headers=read_headers(),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["readings"][0]["device_id"] == "esp32-lab-01"


def test_history_rejects_reversed_time_range(tmp_path):
    response = make_client(tmp_path).get(
        "/api/v1/readings?start=2026-10-23T10:00:00Z&end=2026-10-22T10:00:00Z",
        headers=read_headers(),
    )
    assert response.status_code == 422


def test_history_rejects_timezone_naive_filter(tmp_path):
    response = make_client(tmp_path).get(
        "/api/v1/readings?start=2026-10-22T10:00:00",
        headers=read_headers(),
    )
    assert response.status_code == 422


def test_history_limit_is_bounded(tmp_path):
    client = make_client(tmp_path)
    assert client.get("/api/v1/readings?limit=501", headers=read_headers()).status_code == 422
    assert client.get("/api/v1/readings?limit=0", headers=read_headers()).status_code == 422


def test_invalid_device_filter_is_rejected(tmp_path):
    response = make_client(tmp_path).get(
        "/api/v1/readings?device_id=bad%20id",
        headers=read_headers(),
    )
    assert response.status_code == 422


def test_health_endpoint_does_not_require_credentials(tmp_path):
    assert make_client(tmp_path).get("/healthz").json() == {"status": "ok"}
