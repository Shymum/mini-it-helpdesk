# Mini IT Helpdesk

A standalone Flask and SQLite demonstration for creating, viewing and tracking IT support tickets. Tickets have categories, priorities and editable statuses. Input is checked on the server and stored in a local SQLite database.

## Run locally

Requires Python 3.10 or newer:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. The database is created automatically in `instance/`. Create a fictional request, open it from the list, and change its status. The database persists between restarts.

```bash
python -m pytest -q
```

This is an independent portfolio demo. It has no authentication, access control, CSRF protection, backups or production deployment configuration. Run it locally and use fictional data only; do not expose it to the internet or use it for real support requests.
