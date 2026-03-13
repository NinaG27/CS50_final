from flask import (
    Blueprint,
    render_template,
    request,
    session,
    current_app,
)
from datetime import datetime, date, time
from collections import defaultdict
from .models import ChatLog
from .helpers import login_required
from . import db
from groq import Groq

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


def fetch_messages(user_id, limit=20, today_only=False):
    try:
        query = ChatLog.query.filter_by(user_id=user_id)

        # Filter only todays messages
        if today_only:
            today_midnight = datetime.combine(date.today(), time.min)
            query = query.filter(ChatLog.created_at >= today_midnight)

        messages = query.order_by(ChatLog.created_at.asc()).limit(limit).all()

        # Add greeting message
        if not messages:
            greeting = add_message(
                user_id=user_id,
                role="assistant",
                message="Bonjour ! How can I help you with French today?",
            )
            messages = [greeting]

    except Exception as e:
        return None

    return messages


@main.route("/assistant")
@login_required
def assistant():
    date = datetime.now()

    user_id = session.get("user_id")
    messages = fetch_messages(user_id=user_id, today_only=True)

    return render_template("assistant.html", messages=messages, date=date)


@main.route("/history")
@login_required
def chat_history():
    user_id = session.get("user_id")
    # formatting messages by date
    # from https://docs.python.org/3/library/collections.html#defaultdict-examples
    sorted_messages = defaultdict(list)  # Order not guaranteed need to fix later

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

    return render_template("notes.html", user_notes=user_notes, date=date)


@main.route("/note/<int:note_id>")
@login_required
def load_note(note_id):
    user_id = session.get("user_id")
    try:
        note = get_note(user_id, note_id)
    except:
        return render_template("404.html")

    return render_template("note.html", note=note)


def add_message(user_id, role, message):
    new_message = ChatLog(user_id=user_id, role=role, message=message)

    try:
        db.session.add(new_message)
        db.session.commit()
    except Exception as e:
        print("Error adding message", e)
        return None

    return new_message


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

    # Save user message to db
    user_message = add_message(user_id, "user", user_input)

    if not user_message:
        return {"message": "Error saving user message"}, 400

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
    assistant_message = add_message(user_id, "assistant", assistant_reply)
    if not assistant_message:
        return {"error": "Error saving assistant message"}, 400

    formatted_message = {
        "role": assistant_message.role,
        "message": assistant_message.message,
        "created_at": assistant_message.created_at,
    }
    return {"message": "Success", "assistant_message": formatted_message}, 200


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

#     # Formatting data from Row format to dict (maybe remove id and user id later?) TODO - maybe dont need to format
#     safe_notes = []
#     for note in user_notes:
#         note_dict = dict(note)
#         note_dict["created_at"] = datetime.datetime.fromisoformat(note_dict["created_at"]).strftime("%d/%m/%Y")
#         safe_notes.append(note_dict)

#     return jsonify(safe_notes)
