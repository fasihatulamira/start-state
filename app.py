"""Start State — Flask web app (user form + admin view).

MySQL schema/database: start_state
Table: submissions
"""

from __future__ import annotations

import json
import os
from functools import wraps
from typing import Any

import pymysql
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from pymysql.cursors import DictCursor

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-change-me")

# Database schema name (MySQL "database") and table used by the app
DB_SCHEMA = os.getenv("MYSQL_DATABASE", "start_state")
TABLE_SUBMISSIONS = "submissions"


def db_config() -> dict[str, Any]:
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": DB_SCHEMA,
        "charset": "utf8mb4",
        "cursorclass": DictCursor,
        "autocommit": True,
    }


def get_connection():
    return pymysql.connect(**db_config())


def parse_subunits(raw: Any) -> list[dict[str, str]]:
    if raw is None:
        return []
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            return []
    if not isinstance(raw, list):
        return []
    result: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "subunit_name": str(item.get("subunit_name", "")).strip(),
                "group_list": str(item.get("group_list", "")).strip(),
                "place_name": str(item.get("place_name", "")).strip(),
            }
        )
    return result


def extract_form_payload() -> tuple[str, list[dict[str, str]], str | None]:
    unit_name = (request.form.get("unit_name") or "").strip()
    names = request.form.getlist("subunit_name")
    groups = request.form.getlist("group_list")
    places = request.form.getlist("place_name")

    if not unit_name:
        return "", [], "Unit name is required."

    count = max(len(names), len(groups), len(places))
    if count == 0:
        return unit_name, [], "Add at least one subunit."

    subunits: list[dict[str, str]] = []
    for i in range(count):
        subunit_name = (names[i] if i < len(names) else "").strip()
        group_list = (groups[i] if i < len(groups) else "").strip()
        place_name = (places[i] if i < len(places) else "").strip()

        # Skip completely empty trailing rows
        if not subunit_name and not group_list and not place_name:
            continue

        if not subunit_name:
            return unit_name, [], f"Subunit {i + 1}: name is required."
        if not group_list:
            return unit_name, [], f"Subunit {i + 1}: group list is required."
        if not place_name:
            return unit_name, [], f"Subunit {i + 1}: place name is required."

        subunits.append(
            {
                "subunit_name": subunit_name,
                "group_list": group_list,
                "place_name": place_name,
            }
        )

    if not subunits:
        return unit_name, [], "Add at least one subunit."

    return unit_name, subunits, None


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        unit_name, subunits, error = extract_form_payload()
        if error:
            flash(error, "error")
            return render_template(
                "form.html",
                unit_name=unit_name,
                subunits=subunits or [{"subunit_name": "", "group_list": "", "place_name": ""}],
            )

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"INSERT INTO {TABLE_SUBMISSIONS} (unit_name, subunits) "
                        "VALUES (%s, CAST(%s AS JSON))",
                        (unit_name, json.dumps(subunits, ensure_ascii=False)),
                    )
                    new_id = cur.lastrowid
            flash(f"Saved. Reference #{new_id}", "ok")
            return redirect(url_for("index"))
        except Exception as exc:  # noqa: BLE001 — surface DB setup issues clearly
            flash(f"Could not save: {exc}", "error")
            return render_template("form.html", unit_name=unit_name, subunits=subunits)

    return render_template(
        "form.html",
        unit_name="",
        subunits=[{"subunit_name": "", "group_list": "", "place_name": ""}],
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin"))

    if request.method == "POST":
        password = request.form.get("password") or ""
        expected = os.getenv("ADMIN_PASSWORD", "")
        if expected and password == expected:
            session["is_admin"] = True
            return redirect(url_for("admin"))
        flash("Invalid password.", "error")

    return render_template("admin_login.html")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin():
    submissions: list[dict[str, Any]] = []
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT id, unit_name, subunits, created_at
                    FROM {TABLE_SUBMISSIONS}
                    ORDER BY created_at DESC, id DESC
                    """
                )
                rows = cur.fetchall()
        for row in rows:
            submissions.append(
                {
                    "id": row["id"],
                    "unit_name": row["unit_name"],
                    "subunits": parse_subunits(row["subunits"]),
                    "created_at": row["created_at"],
                }
            )
    except Exception as exc:  # noqa: BLE001
        flash(f"Could not load submissions: {exc}", "error")

    return render_template("admin.html", submissions=submissions)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
