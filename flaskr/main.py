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
    # formatting messages by date 
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


# ///////////////////////// TO FIX

#  @app.route("/api/send_message", methods=["POST"])
#     @login_required
#     def send_message():
#         # From https://console.groq.com/docs/quickstart
#         api_key = current_app.config("GROQ_API_KEY")

#         groq_client = Groq(api_key=api_key)

#         # Login required decorator checks the user id validity
#         user_id = session.get("user_id")
#         user_input = request.get_json().get("message")

#         # Save user message to db
#         message_id = save_message(db, user_id, "user", user_input)
      

#         if not message_id:
#            return "TODO error with writing message to bd"
        
#         SYSTEM_PROMPT = """
#                 You are a friendly French language learning assistant.

#                 Rules:
#                 - Teach French clearly and simply
#                 - Use short explanations
#                 - Give examples when helpful
#                 - Correct mistakes gently
#                 - If the user asks in English, explain in English
#                 - If the user asks in French, respond in simple French
#                 - Adapt explanations to a beginner level
#                 """
        # # Get last 20 messages 
        # history =  ChatLog.query.filter_by(user_id).limit(20).order_by("created_at", "DESC")


        # # Create history for prompt 
        # messages=[
        #     {
        #         "role": "system",
        #         "content": SYSTEM_PROMPT,
        #     },
        # ]
        
        # # Add last 20 messages 
        # for message in history:
        #     messages.append({         
        #         "role": message["role"],
        #         "content": message["message"],
        #     })

        # # Add current user input
        # messages.append({
        #     "role": "user",
        #     "content": user_input
        # })

        # # Prompt groq
        # chat_completion = groq_client.chat.completions.create(
        #     messages=messages,
        #     model="llama-3.3-70b-versatile",
        # )

        # assistant_reply = chat_completion.choices[0].message.content

        # # Save assistant reply to db
        # save_message(db, user_id, "assistant", assistant_reply)
        # db.commit()

        # return jsonify({"reply" : assistant_reply})
    
    # @app.route("/api/notes", methods=["POST"])
    # @login_required
    # def add_note():
    #     user_id = session.get("user_id")

    #     user_input = request.get_json().get("note")

    #     db = get_db()
    #     # Save user note to db
    #     save_note(db, user_id, user_input)
    #     db.commit()
        
    #     print("writing note", user_input)

    #     return jsonify({"status": "success"})
    
    # @app.route("/api/notes/<int:note_id>", methods=["DELETE"])
    # @login_required
    # def delete_note_api(note_id):
    #     user_id = session.get("user_id")

    #     db = get_db()
    #     # Delete note from db
    #     delete_note(db, user_id, note_id)
    #     db.commit()

    #     return jsonify({"status": "deleted"})
    
    # @app.route("/api/notes/<int:note_id>", methods=["PATCH"])
    # @login_required
    # def update_note_api(note_id):
    #     user_id = session.get("user_id")
    #     new_note = request.get_json().get("note")

    #     db = get_db()
    #     # Edit note in db
    #     update_user_note(db, user_id, note_id, new_note)
    #     db.commit()

    #     return jsonify({"status": "deleted"})
    
    # @app.route("/api/get_notes")
    # @login_required
    # def get_notes():
    #     user_id = session.get("user_id")

    #     user_notes = get_user_notes(user_id)
         
    #     # Formating data from Row format to dict (maybe remove id and user id later?) TODO - mybe dont need to format
    #     safe_notes = []
    #     for note in user_notes:
    #         note_dict = dict(note)
    #         note_dict["created_at"] = datetime.datetime.fromisoformat(note_dict["created_at"]).strftime("%d/%m/%Y")
    #         safe_notes.append(note_dict)

    #     return jsonify(safe_notes)
