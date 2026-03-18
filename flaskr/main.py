from flask import (
    Blueprint,
    render_template,
    request,
    session,
    current_app,
)
from datetime import datetime, date, time
from collections import defaultdict
from .models import ChatLog, UserNotes
from .helpers import login_required
from . import db
from groq import Groq

main = Blueprint("main", __name__)


@main.route("/")
def index():
    if session.get("user_id"):
        return assistant()
    return render_template("index.html")


### Assistant page routes ###


def fetch_messages(user_id, limit=20, today_only=False):
    query = ChatLog.query.filter_by(user_id=user_id)

    # Filter only todays messages
    if today_only:
        today_midnight = datetime.combine(date.today(), time.min)
        query = query.filter(ChatLog.created_at >= today_midnight)

    messages = query.order_by(ChatLog.created_at.asc()).limit(limit).all()

    # Add greeting message // should move to frontend in the future
    if not messages:
        greeting = add_message(
            user_id=user_id,
            role="assistant",
            message="Bonjour ! How can I help you with French today?",
        )
        messages = [greeting]

    return messages


@main.route("/assistant")
@login_required
def assistant():
    user_id = session.get("user_id")
    date = datetime.now()

    try:
        messages = fetch_messages(user_id=user_id, today_only=True)
    except Exception as e:
        db.session.rollback()
        print("Critical error", {e})
        return render_template("500.html")

    return render_template("assistant.html", messages=messages, date=date)


@main.route("/api/send_message", methods=["POST"])
@login_required
def send_message():
    # From https://console.groq.com/docs/quickstart
    api_key = current_app.config.get("GROQ_API_KEY")

    groq_client = Groq(api_key=api_key)

    # Login required decorator checks the user id validity
    user_id = session.get("user_id")
    user_input = request.get_json().get("message")

    if not user_input:
        return {"error": "Message body cannot be empty"}, 400

    try:
        # Save user message to db
        user_message = add_message(user_id, "user", user_input)

        if not user_message:
            return {"message": "Error saving user message"}, 400
    except Exception as e:
        db.session.rollback()
        print("Critical error:", {e})
        return {"error": "Internal Server Error"}, 500

    SYSTEM_PROMPT = """
                You are a friendly French language learning assistant.

                Rules:
                - Teach French clearly and simply
                - Use short explanations
                - Give examples when helpful
                - Correct mistakes gently
                - If the user asks in English, explain in English
                - If the user asks in French, respond in simple French
                - Adapt explanations to a beginner level
                """
    # Get last 20 messages - fixed for now
    history = fetch_messages(user_id, limit=20, today_only=True)

    if not history:
        return {"error": "Error getting user history"}, 400

    # Create history for prompt
    messages = [
        {
            "role": "assistant",
            "content": SYSTEM_PROMPT,
        },
    ]

    # Add last 20 messages
    for message in history:
        messages.append(
            {
                "role": message.role,
                "content": message.message,
            }
        )

    # Prompt groq
    chat_completion = groq_client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
    )

    assistant_reply = chat_completion.choices[0].message.content

    # Save assistant reply to db
    try:
        assistant_message = add_message(user_id, "assistant", assistant_reply)
        if not assistant_message:
            return {"error": "Error saving assistant message"}, 400
    except Exception as e:
        db.session.rollback()
        print("Critical error:", {e})
        return {"error": "Internal Server Error"}, 500

    formatted_message = {
        "role": assistant_message.role,
        "message": assistant_message.message,
        "created_at": assistant_message.created_at,
    }
    return {"message": "Success", "assistant_message": formatted_message}, 200


def add_message(user_id, role, message):
    new_message = ChatLog(user_id=user_id, role=role, message=message)

    db.session.add(new_message)
    db.session.commit()

    return new_message


### History page routes ###


@main.route("/history")
@login_required
def chat_history():
    user_id = session.get("user_id")

    # formatting messages by date
    # from https://docs.python.org/3/library/collections.html#defaultdict-examples
    sorted_messages = defaultdict(list)

    try:
        for msg in fetch_messages(user_id=user_id):
            date = msg.created_at.strftime("%Y-%m-%d")
            sorted_messages[date].append(msg)

        return render_template("history.html", messages=sorted_messages)
    except Exception as e:
        db.session.rollback()
        print("Critical error", {e})
        return render_template("500.html")


### Notes page routes ###


def get_user_notes(user_id):
    notes = UserNotes.query.filter_by(user_id=user_id).all()

    formatted_notes = [
        {
            "id": note.id,
            "note": note.note,
            "created_at": note.created_at,
        }
        for note in notes
    ]

    return formatted_notes


@main.route("/notes")
@login_required
def notes():
    user_id = session.get("user_id")
    date = datetime.now().date()

    try:
        user_notes = get_user_notes(user_id)
        return render_template("notes.html", user_notes=user_notes, date=date)
    except Exception as e:
        print("Critical error:", {e})
        return render_template("500.html"), 500


@main.route("/note/<int:note_id>")
@login_required
def load_note(note_id):
    user_id = session.get("user_id")
    try:
        note = UserNotes.query.filter_by(user_id=user_id, id=note_id).first()

        if not note:
            return render_template("404.html"), 400

        formatted_note = {
            "id": note.id,
            "note": note.note,
            "created_at": note.created_at,
        }

        return render_template("note.html", note=formatted_note)

    except Exception as e:
        print("Critical error:", {e})
        return render_template("500.html"), 500


@main.route("/api/notes", methods=["POST"])
@login_required
def add_note():
    user_id = session.get("user_id")
    user_input = request.get_json().get("note")

    if not user_input or user_input.strip() == "":
        return {"error": "Note content cannot be empty"}, 400

    try:
        new_note = UserNotes(user_id=user_id, note=user_input)

        db.session.add(new_note)
        db.session.commit()

        return {"message": "Success"}, 201

    except Exception as e:
        db.session.rollback()
        print("Critical error:", {e})
        return {"error": "Internal Server Error"}, 500


@main.route("/api/notes/<int:note_id>", methods=["DELETE"])
@login_required
def delete_note_api(note_id):
    user_id = session.get("user_id")

    try:
        to_delete = UserNotes.query.filter_by(id=note_id, user_id=user_id).first()

        if not to_delete:
            return {"error": "Note not found or unauthorized"}, 404

        db.session.delete(to_delete)
        db.session.commit()

        return {"message": "success"}, 200
    except Exception as e:
        db.session.rollback()
        print("Critical error:", {e})
        return {"error": "Internal Server Error"}, 500


@main.route("/api/notes/<int:note_id>", methods=["PATCH"])
@login_required
def update_note_api(note_id):
    user_id = session.get("user_id")
    new_note = request.get_json().get("note")

    try:
        note = UserNotes.query.filter_by(id=note_id, user_id=user_id).first()

        if not note:
            return {"error": "Note not found or unauthorized"}, 404

        note.note = new_note
        db.session.commit()

        return {"message": "success"}, 200
    except Exception as e:
        db.session.rollback()
        print("Critical error:", {e})
        return {"error": "Internal Server Error"}, 500


@main.route("/api/get_notes")
@login_required
def get_notes():
    user_id = session.get("user_id")

    try:
        user_notes = get_user_notes(user_id)
        return {"message": "success", "user_notes": user_notes}, 200
    except Exception as e:
        print("Critical error:", {e})
        return {"error": "Internal Server Error"}, 500
