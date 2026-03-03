from flask import Blueprint, Flask, render_template, request, url_for, g, session, redirect, current_app, jsonify
from flask_login import login_required
import os
from dotenv import load_dotenv
import datetime
from collections import defaultdict

from flaskr.db import add_user, auth_user, save_message, get_messages, get_user_notes, save_note, delete_note, get_note, update_user_note
from flaskr.helpers import login_required

from groq import Groq

main = Blueprint('main', __name__)

@main.route("/")
def index():
    return render_template("index.html")
    
@main.route("/assistant")
@login_required
def assistant():
    date = datetime.datetime.now().date()
    # temp for styling test
    user_id = session.get("user_id")
    messages = get_messages(user_id)
    ######
    return render_template("assistant.html", messages=messages, date=date)

@main.route("/history")
@login_required
def chat_history():
    user_id = session.get("user_id")
    # formating messages by date 
    # from https://docs.python.org/3/library/collections.html#defaultdict-examples
    sorted_messages = defaultdict(list) # Order not guaranteed need to fix later 

    for msg in get_messages(user_id):
        # https://note.nkmk.me/en/python-datetime-isoformat-fromisoformat/
        date = datetime.datetime.fromisoformat(msg["created_at"]).date()
        sorted_messages[date].append(msg)

    return render_template("history.html", messages=sorted_messages)

@main.route("/notes")
@login_required
def notes():
    user_id = session.get("user_id")
    date = datetime.datetime.now().date()
    try:
        user_notes = get_user_notes(user_id)
    except: 
        return render_template("404.html")

    return render_template("notes.html",user_notes=user_notes, date=date)

@main.route("/note/<int:note_id>")
@login_required
def load_note(note_id):
    user_id = session.get("user_id")
    try:
        note = get_note(user_id, note_id)
    except:
        return render_template("404.html")
        
    return render_template("note.html", note=note)