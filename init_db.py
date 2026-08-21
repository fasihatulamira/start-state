"""Create tables inside MySQL schema `start_state`."""

from __future__ import annotations

import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
SCHEMA_SQL = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")


def main() -> None:
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")

    # Connect without selecting a DB so CREATE DATABASE works
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            for statement in SCHEMA_SQL.split(";"):
                sql = statement.strip()
                # skip empty / comment-only chunks
                lines = [
                    line
                    for line in sql.splitlines()
                    if line.strip() and not line.strip().startswith("--")
                ]
                cleaned = "\n".join(lines).strip()
                if cleaned:
                    cur.execute(cleaned)
        print("OK: schema `start_state` and table `submissions` are ready.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
