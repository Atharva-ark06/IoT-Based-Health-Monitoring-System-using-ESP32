from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.app import create_app
from simulator.device_simulator import build_signed_request

DEVICE_SECRET = "test-simulator-secret-not-for-production"
READ_TOKEN = "test-read-token-not-for-production"


def test_simulator_request_is_accepted_and_readable(tmp_path):
    client = TestClient(
        create_app(
            db_path=str(tmp_path / "readings.sqlite3"),
            device_secret=DEVICE_SECRET,
            read_token=READ_TOKEN,
        )
    )
    reading = {
        "device_id": "esp32-sim-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": 36.6,
        "bpm": 74,
    }
    body, headers = build_signed_request(
        DEVICE_SECRET, reading, timestamp=str(int(time.time())),
        nonce="simulator-test-nonce-0001",
    )

    response = client.post("/api/v1/readings", content=body, headers=headers)
    assert response.status_code == 201
    history = client.get(
        "/api/v1/readings",
        headers={"Authorization": f"Bearer {READ_TOKEN}"},
    )
    assert history.status_code == 200
    assert history.json()["readings"][0]["device_id"] == "esp32-sim-01"
    assert history.json()["readings"][0]["bpm"] == 74


def test_simulator_signs_exact_serialized_body():
    reading = {"device_id": "esp32-sim-01", "timestamp": "2026-10-24T00:00:00+00:00",
               "temperature": 36.5, "bpm": 70}
    body, headers = build_signed_request(
        DEVICE_SECRET, reading, timestamp="1792800000", nonce="fixed-test-nonce-0001"
    )
    assert json.loads(body) == reading
    assert len(headers["X-Device-Signature"]) == 64
    assert headers["X-Device-Nonce"] == "fixed-test-nonce-0001"


def test_simulator_requires_secret():
    try:
        build_signed_request("", {"device_id": "esp32-sim-01"})
    except ValueError as error:
        assert "secret" in str(error).lower()
    else:
        raise AssertionError("empty secret should be rejected")
