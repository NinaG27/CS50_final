import sqlite3
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

import click
from flask import current_app, g

# From https://flask.palletsprojects.com/en/stable/tutorial/database/
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# Take application instance and register functions since instance not available in this file 
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db
        
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# From https://flask.palletsprojects.com/en/stable/patterns/sqlite3/#easy-querying
def query_db(query, args=(), one=False):
    """Query database """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    return {}, 200
    

def add_user(db, email, password):
    # Hash password 
    password_hash = generate_password_hash(password)
    # INSERT OR IGNORE can silently fail so need to check for changes
    cursor = db.execute("INSERT OR IGNORE INTO users (email, password_hash) VALUES (?, ?)", (email, password_hash))

    return cursor.rowcount == 1

def find_user(email):

    user = query_db("SELECT * FROM users WHERE email = ?", [email], True)

    return user if user else None
  
def auth_user(email, password):
    # TODO add try catch block 
    user = find_user(email)

    # Check if user exists
    if not user: 
        return "User does not exist"
    
    hashed_password = user["password_hash"]
    match = check_password_hash(hashed_password, password)

    if match:
        return user
    else:
        print("password or username do not match")
        return "TODO password or username do not match"


# Inconsistant returns might need to consolidate later 
