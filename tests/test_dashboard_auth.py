from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.app import _signature, create_app

DEVICE_SECRET = "test-device-secret-not-for-production"
DASHBOARD_PASSWORD = "test-dashboard-password-not-for-production"
SESSION_SECRET = "test-session-secret-long-enough-for-tests-0123456789"


def make_client(tmp_path):
    app = create_app(
        db_path=str(tmp_path / "readings.sqlite3"),
        device_secret=DEVICE_SECRET,
        read_token="separate-server-read-token",
        dashboard_password=DASHBOARD_PASSWORD,
        session_secret=SESSION_SECRET,
        dashboard_origin="http://testserver",
        secure_cookies=False,
    )
    return TestClient(app)


def signed_reading(client, nonce: str = "dashboard-test-nonce-0001"):
    body = json.dumps(
        {
            "device_id": "esp32-dashboard-test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "temperature": 36.7,
            "bpm": 77,
        },
        separators=(",", ":"),
    ).encode()
    timestamp = str(int(time.time()))
    headers = {
        "Content-Type": "application/json",
        "X-Device-Timestamp": timestamp,
        "X-Device-Nonce": nonce,
        "X-Device-Signature": _signature(DEVICE_SECRET, timestamp, nonce, body),
    }
    return client.post("/api/v1/readings", content=body, headers=headers)


def test_dashboard_history_requires_session_cookie(tmp_path):
    client = make_client(tmp_path)
    assert client.get("/api/v1/dashboard/readings").status_code == 401


def test_login_issues_http_only_same_site_session_and_dashboard_reads_data(tmp_path):
    client = make_client(tmp_path)
    assert signed_reading(client).status_code == 201
    response = client.post(
        "/api/v1/dashboard/login",
        json={"password": DASHBOARD_PASSWORD},
        headers={"Origin": "http://testserver"},
    )
    assert response.status_code == 200
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=strict" in cookie
    assert "iot_dashboard_session=" in cookie

    history = client.get("/api/v1/dashboard/readings")
    assert history.status_code == 200
    assert history.json()["readings"][0]["device_id"] == "esp32-dashboard-test"


def test_wrong_password_and_cross_origin_login_are_rejected(tmp_path):
    client = make_client(tmp_path)
    wrong_password = client.post(
        "/api/v1/dashboard/login",
        json={"password": "wrong"},
        headers={"Origin": "http://testserver"},
    )
    assert wrong_password.status_code == 401
    wrong_origin = client.post(
        "/api/v1/dashboard/login",
        json={"password": DASHBOARD_PASSWORD},
        headers={"Origin": "https://attacker.example"},
    )
    assert wrong_origin.status_code == 403


def test_dashboard_logout_invalidates_cookie(tmp_path):
    client = make_client(tmp_path)
    login = client.post(
        "/api/v1/dashboard/login",
        json={"password": DASHBOARD_PASSWORD},
        headers={"Origin": "http://testserver"},
    )
    assert login.status_code == 200
    assert client.get("/api/v1/dashboard/readings").status_code == 200
    logout = client.post(
        "/api/v1/dashboard/logout",
        json={},
        headers={"Origin": "http://testserver"},
    )
    assert logout.status_code == 200
    assert client.get("/api/v1/dashboard/readings").status_code == 401


def test_dashboard_login_fails_closed_when_secrets_are_not_configured(tmp_path):
    client = TestClient(
        create_app(
            db_path=str(tmp_path / "readings.sqlite3"),
            dashboard_origin="http://testserver",
            secure_cookies=False,
        )
    )
    response = client.post(
        "/api/v1/dashboard/login",
        json={"password": "anything"},
        headers={"Origin": "http://testserver"},
    )
    assert response.status_code == 503


def test_dashboard_pages_send_security_headers(tmp_path):
    client = make_client(tmp_path)
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "default-src 'self'" in response.headers["content-security-policy"]
    assert response.headers["cache-control"] == "no-store"
    script = client.get("/dashboard.js")
    assert script.status_code == 200
    assert "text/javascript" in script.headers["content-type"]
