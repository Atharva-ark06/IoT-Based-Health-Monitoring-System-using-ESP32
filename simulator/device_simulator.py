"""Hardware-free ESP32 ingestion simulator for local integration testing.

The simulator sends the same HMAC-SHA256 envelope expected from the API.
It generates synthetic readings only; these are not real or medical data.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def build_signed_request(
    secret: str,
    reading: dict[str, object],
    *,
    timestamp: str | None = None,
    nonce: str | None = None,
) -> tuple[bytes, dict[str, str]]:
    """Serialize once, then sign the exact bytes sent over the wire."""
    if not secret:
        raise ValueError("A non-empty device HMAC secret is required")
    sent_at = timestamp or str(int(time.time()))
    request_nonce = nonce or secrets.token_hex(16)
    body = json.dumps(reading, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    message = sent_at.encode("ascii") + b"." + request_nonce.encode("ascii") + b"." + body
    signature = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return body, {
        "Content-Type": "application/json",
        "X-Device-Timestamp": sent_at,
        "X-Device-Nonce": request_nonce,
        "X-Device-Signature": signature,
    }


def send_reading(url: str, secret: str, reading: dict[str, object], timeout: float = 5.0) -> int:
    parsed = urlparse(url)
    if parsed.scheme != "https" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Use HTTPS except for loopback-only local development")
    body, headers = build_signed_request(secret, reading)
    request = Request(url, data=body, headers=headers, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            # Do not print response bodies or sensor payloads.
            return response.status
    except HTTPError as error:
        return error.code
    except URLError as error:
        raise RuntimeError("Could not reach ingestion API") from error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000/api/v1/readings")
    parser.add_argument("--device-id", default="esp32-sim-01")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()
    if not 1 <= args.count <= 1000:
        parser.error("--count must be between 1 and 1000")
    if not 0 <= args.interval <= 3600:
        parser.error("--interval must be between 0 and 3600 seconds")
    secret = os.getenv("IOT_DEVICE_HMAC_SECRET", "")
    if not secret:
        parser.error("Set IOT_DEVICE_HMAC_SECRET in the environment")

    for index in range(args.count):
        reading = {
            "device_id": args.device_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            # Synthetic example values only; no physical sensor is connected.
            "temperature": round(36.5 + (index % 5) * 0.1, 1),
            "bpm": 72 + (index % 8),
        }
        try:
            status = send_reading(args.url, secret, reading)
        except (ValueError, RuntimeError) as error:
            print(f"Request failed: {error}")
            return 1
        print(f"Reading {index + 1}/{args.count}: HTTP {status}")
        if not 200 <= status < 300:
            return 1
        if index + 1 < args.count:
            time.sleep(args.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
