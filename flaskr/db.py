import sqlite3
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
import click
from flask import current_app, g

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)


# From https://flask.palletsprojects.com/en/stable/patterns/sqlite3/#easy-querying
def query_db(query, args=(), one=False):
    """Query database """
    # cur = get_db().execute(query, args)
    # rv = cur.fetchall()
    # cur.close()
    # return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    return {}, 200
    

def add_user(db, email, password):
    cursor = db.execute("INSERT OR IGNORE INTO users (email, password_hash) VALUES (?, ?)", [email, password])

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

# Save user and assistant messages 
def save_message(db, user_id, role, message):

    cursor = db.execute("INSERT INTO chat_log (user_id, role, message) VALUES (?, ?, ?)", [user_id, role, message])

    return cursor.rowcount == 1

def save_note(db, user_id, note):
    cursor = db.execute("INSERT INTO user_notes (user_id, note) VALUES (?, ?)", [user_id, note])

    return cursor.rowcount == 1

def delete_note(db, user_id, id):
    cursor = db.execute("DELETE FROM user_notes WHERE user_id=? AND id=?", [user_id, id])

    return cursor.rowcount == 1

def update_user_note(db, user_id, id, new_note):
    cursor = db.execute("UPDATE user_notes SET note=? WHERE user_id=? AND id=?", [new_note, user_id, id])

    return cursor.rowcount == 1

def get_messages(user_id, limit=20):
    messages = query_db("SELECT * FROM chat_log WHERE user_id=? ORDER BY created_at DESC LIMIT ?", [user_id, limit])
    # list[start : stop : step]
    return messages[::-1]
# Inconsistent returns might need to consolidate later 

def get_user_notes(user_id):
    notes = query_db("SELECT * FROM user_notes WHERE user_id=? ORDER BY created_at DESC", [user_id])
    
    if notes is None:
        raise Exception("Database error fetching notes")

    return notes[::-1] or [] # Add this pattern to other methods? 


def get_note(user_id, id):
    note = query_db("SELECT * FROM user_notes WHERE user_id=? AND id=?", [user_id, id])
    
    if note is None:
        raise Exception("Database error fetching note")

    return note[0]
