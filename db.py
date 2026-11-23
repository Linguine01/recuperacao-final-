import os
import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


def close_db(_error=None):
    connection = g.pop('db', None)
    if connection is not None:
        connection.close()


def init_app(app):
    database = Path(os.environ.get('MEDTEC_DB') or Path(app.instance_path) / 'medtec.sqlite3')
    database.parent.mkdir(parents=True, exist_ok=True)
    app.config['DATABASE'] = database
    app.teardown_appcontext(close_db)
    with app.app_context():
        schema = Path(app.root_path) / 'schema.sql'
        get_db().executescript(schema.read_text(encoding='utf-8'))
