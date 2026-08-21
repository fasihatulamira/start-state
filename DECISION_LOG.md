# Decision Log — Start State

## 2026-08-20 — Switch to Python (Flask)

### Stack
- **Flask + Jinja2 templates + static CSS** (replaced earlier Next.js scaffold).
- **PyMySQL** against MySQL schema `start_state`.
- **python-dotenv** for local `.env` config.

### Data model
- Clarification: `start_state` is the **schema/database** name (not the table).
- Table inside that schema: `submissions`.
- One row per form: `id`, `unit_name`, `subunits` (JSON), `created_at`.
- Subunit object: `{ subunit_name, group_list, place_name }`.
- Init script: `init_db.py` / `sql/schema.sql`.

### Auth
- Admin password from `ADMIN_PASSWORD`.
- Flask session cookie (`FLASK_SECRET_KEY`); `/admin` requires login.

### Routes
- `GET/POST /` — user form
- `GET/POST /admin/login` — admin login
- `GET /admin` — list submissions
- `POST /admin/logout` — clear session

### QA
- Pass: `.env` configured; `python init_db.py` created schema `start_state` + table `submissions` (`id`, `unit_name`, `subunits`, `created_at`).
