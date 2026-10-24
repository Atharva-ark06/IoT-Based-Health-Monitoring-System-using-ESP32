"""Safe SQLite backup and retention maintenance helpers.

Destructive pruning is opt-in and requires a backup path.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backend.app import _connect


def backup_database(source_path: str, backup_path: str) -> Path:
    source = Path(source_path).resolve()
    destination = Path(backup_path).resolve()
    if source == destination:
        raise ValueError("Backup path must differ from the source database")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError("Backup destination already exists; choose a new path")
    with closing(_connect(str(source))) as source_connection:
        with sqlite3.connect(str(destination)) as destination_connection:
            source_connection.backup(destination_connection)
    try:
        os.chmod(destination, 0o600)
    except OSError:
        # Filesystem permission semantics vary across platforms; document host-level controls.
        pass
    return destination


def retention_counts(database_path: str, retention_days: int, now: datetime | None = None) -> dict[str, int]:
    if retention_days < 1:
        raise ValueError("retention_days must be at least 1")
    current = now or datetime.now(timezone.utc)
    cutoff = (current.astimezone(timezone.utc) - timedelta(days=retention_days)).isoformat()
    nonce_cutoff = int(current.timestamp()) - 600
    with closing(_connect(database_path)) as connection:
        readings = connection.execute(
            "SELECT COUNT(*) FROM readings WHERE received_at < ?", (cutoff,)
        ).fetchone()[0]
        audits = connection.execute(
            "SELECT COUNT(*) FROM audit_events WHERE occurred_at < ?", (cutoff,)
        ).fetchone()[0]
        nonces = connection.execute(
            "SELECT COUNT(*) FROM used_nonces WHERE seen_at < ?", (nonce_cutoff,)
        ).fetchone()[0]
    return {"readings": readings, "audit_events": audits, "expired_nonces": nonces}


def prune_database(database_path: str, retention_days: int, now: datetime | None = None) -> dict[str, int]:
    if retention_days < 1:
        raise ValueError("retention_days must be at least 1")
    current = now or datetime.now(timezone.utc)
    cutoff = (current.astimezone(timezone.utc) - timedelta(days=retention_days)).isoformat()
    nonce_cutoff = int(current.timestamp()) - 600
    with closing(_connect(database_path)) as connection, connection:
        readings = connection.execute(
            "DELETE FROM readings WHERE received_at < ?", (cutoff,)
        ).rowcount
        audits = connection.execute(
            "DELETE FROM audit_events WHERE occurred_at < ?", (cutoff,)
        ).rowcount
        nonces = connection.execute(
            "DELETE FROM used_nonces WHERE seen_at < ?", (nonce_cutoff,)
        ).rowcount
    return {"readings": readings, "audit_events": audits, "expired_nonces": nonces}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default=os.getenv("IOT_DATABASE_PATH", "data/readings.sqlite3"))
    parser.add_argument("--retention-days", type=int, default=90)
    parser.add_argument("--apply", action="store_true", help="perform deletion; requires --backup-path")
    parser.add_argument("--backup-path", help="new path for a SQLite online backup before pruning")
    args = parser.parse_args()

    if args.retention_days < 1:
        parser.error("--retention-days must be at least 1")
    if args.apply and not args.backup_path:
        parser.error("--apply requires --backup-path so a backup is created first")

    if args.backup_path:
        try:
            destination = backup_database(args.database, args.backup_path)
        except (OSError, sqlite3.Error, ValueError) as error:
            parser.error(f"backup failed: {error}")
        print(f"Backup created: {destination}")

    counts = retention_counts(args.database, args.retention_days)
    print(f"Retention preview (older than {args.retention_days} days): {counts}")
    if args.apply:
        deleted = prune_database(args.database, args.retention_days)
        print(f"Retention applied after backup: {deleted}")
    else:
        print("Dry run only; add --apply and --backup-path to delete anything.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
