# Start State (Python)

Flask web app: users submit a start-state form; admins view submissions.

- **MySQL schema (database):** `start_state`
- **Table:** `submissions`

## Setup

1. Copy env and set your MySQL password + admin password:

```bash
copy .env.example .env
```

2. Create venv and install (if needed):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Create the table inside schema `start_state`:

```bash
python init_db.py
```

Or:

```bash
mysql -u root -p < sql/schema.sql
```

4. Run the app:

```bash
python app.py
```

Open http://127.0.0.1:5000 (form) and http://127.0.0.1:5000/admin (admin).

## Form fields

- Unit name
- One or more subunits, each with:
  - Subunit name
  - Group list
  - Place name
