from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_container_runs_as_non_root_and_has_healthcheck():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "USER app:app" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "IOT_DATABASE_PATH=/app/data/readings.sqlite3" in dockerfile


def test_compose_requires_secrets_and_binds_only_to_loopback():
    compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
    for name in (
        "IOT_DEVICE_HMAC_SECRET",
        "IOT_READ_API_TOKEN",
        "IOT_DASHBOARD_PASSWORD",
        "IOT_SESSION_SECRET",
        "IOT_DASHBOARD_ORIGIN",
    ):
        assert f"${{{name}:?" in compose
    assert '"127.0.0.1:8000:8000"' in compose
    assert "IOT_COOKIE_SECURE: \"true\"" in compose
    assert "iot-data:/app/data" in compose
    assert "no-new-privileges:true" in compose
    assert "cap_drop:" in compose
    assert "read_only: true" in compose
    assert "privileged: true" not in compose


def test_dockerignore_excludes_local_secrets_and_data():
    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
    assert ".env" in dockerignore
    assert "data" in dockerignore
    assert "firmware/**/secrets.h" in dockerignore
    assert "*.sqlite3" in dockerignore
