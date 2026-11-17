"""A small standalone demo helpdesk backed by SQLite."""
import os
import sqlite3
from pathlib import Path
from flask import Flask, abort, g, redirect, render_template, request, url_for

CATEGORIES = ('Hardware', 'Software', 'Access', 'Other')
PRIORITIES = ('Low', 'Medium', 'High')
STATUSES = ('Open', 'In progress', 'Resolved')


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DATABASE=os.path.join(app.instance_path, 'helpdesk.sqlite3'))
    if test_config:
        app.config.update(test_config)
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)

    def db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(error):
        connection = g.pop('db', None)
        if connection is not None:
            connection.close()

    with app.app_context():
        db().execute('''CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL,
            category TEXT NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        db().commit()

    @app.route('/')
    def index():
        tickets = db().execute('SELECT * FROM tickets ORDER BY id DESC').fetchall()
        return render_template('index.html', tickets=tickets)

    @app.route('/tickets/new', methods=['GET', 'POST'])
    def new_ticket():
        errors = []
        values = request.form
        if request.method == 'POST':
            title = values.get('title', '').strip()
            description = values.get('description', '').strip()
            category = values.get('category', '')
            priority = values.get('priority', '')
            if not 3 <= len(title) <= 120:
                errors.append('Title must contain 3–120 characters.')
            if not 10 <= len(description) <= 2000:
                errors.append('Description must contain 10–2000 characters.')
            if category not in CATEGORIES or priority not in PRIORITIES:
                errors.append('Choose a valid category and priority.')
            if not errors:
                cursor = db().execute('INSERT INTO tickets (title, description, category, priority, status) VALUES (?, ?, ?, ?, ?)', (title, description, category, priority, 'Open'))
                db().commit()
                return redirect(url_for('ticket', ticket_id=cursor.lastrowid))
        return render_template('new.html', errors=errors, values=values, categories=CATEGORIES, priorities=PRIORITIES), 400 if errors else 200

    @app.route('/tickets/<int:ticket_id>', methods=['GET', 'POST'])
    def ticket(ticket_id):
        item = db().execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
        if item is None:
            abort(404)
        if request.method == 'POST':
            status = request.form.get('status', '')
            if status not in STATUSES:
                abort(400)
            db().execute('UPDATE tickets SET status = ? WHERE id = ?', (status, ticket_id))
            db().commit()
            return redirect(url_for('ticket', ticket_id=ticket_id))
        return render_template('ticket.html', item=item, statuses=STATUSES)

    return app


if __name__ == '__main__':
    create_app().run(debug=False)
