from flask import Flask, current_app, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import datetime
from flaskr.db import save_message, get_messages, get_user_notes, save_note, delete_note, update_user_note
from flaskr.helpers import login_required
from groq import Groq

# Initialize SQLAlchemy instance 
db = SQLAlchemy()

# from https://flask.palletsprojects.com/en/stable/tutorial/factory/
def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # TODO figure out how sensitive keys need to be added 
    load_dotenv()

    # Configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite',
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
        GROQ_API_KEY=os.getenv("GROQ_API_KEY")
    )

    if test_config is None:
        # load the instance config, if it exists  (when deploying, this can be used to set a real SECRET_KEY. https://flask.palletsprojects.com/en/stable/tutorial/factory/)
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions with app
    db.init_app(app)

    from . import models

    with app.app_context():
        db.create_all()  

    # From https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
    # Registar blueprints 
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    @app.route("/api/send_message", methods=["POST"])
    @login_required
    def send_message():
        # From https://console.groq.com/docs/quickstart
        api_key = current_app.config("GROQ_API_KEY")
        DATABASE = current_app.config["DATABASE"]

        groq_client = Groq(api_key=api_key)

        # TODO Get user id safly? 
        user_id = session.get("user_id")
        user_input = request.get_json().get("message")

        db = get_db()
        # Save user message to db
        message_id = save_message(db, user_id, "user", user_input)
        db.commit()

        if not message_id:
           return "TODO error with writing message to bd"
        
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
        # Get last 20 messages 
        history = get_messages(user_id)

        # Create history for prompt 
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
        ]
        
        # Add last 20 messages 
        for message in history:
            messages.append({         
                "role": message["role"],
                "content": message["message"],
            })

        # Add current user input
        messages.append({
            "role": "user",
            "content": user_input
        })

        # Prompt groq
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
        )

        assistant_reply = chat_completion.choices[0].message.content

        # Save assistant reply to db
        save_message(db, user_id, "assistant", assistant_reply)
        db.commit()

        return jsonify({"reply" : assistant_reply})
    
    @app.route("/api/notes", methods=["POST"])
    @login_required
    def add_note():
        user_id = session.get("user_id")

        user_input = request.get_json().get("note")

        db = get_db()
        # Save user note to db
        save_note(db, user_id, user_input)
        db.commit()
        
        print("writing note", user_input)

        return jsonify({"status": "success"})
    
    @app.route("/api/notes/<int:note_id>", methods=["DELETE"])
    @login_required
    def delete_note_api(note_id):
        user_id = session.get("user_id")

        db = get_db()
        # Delete note from db
        delete_note(db, user_id, note_id)
        db.commit()

        return jsonify({"status": "deleted"})
    
    @app.route("/api/notes/<int:note_id>", methods=["PATCH"])
    @login_required
    def update_note_api(note_id):
        user_id = session.get("user_id")
        new_note = request.get_json().get("note")

        db = get_db()
        # Edit note in db
        update_user_note(db, user_id, note_id, new_note)
        db.commit()

        return jsonify({"status": "deleted"})
    
    @app.route("/api/get_notes")
    @login_required
    def get_notes():
        user_id = session.get("user_id")

        user_notes = get_user_notes(user_id)
         
        # Formating data from Row format to dict (maybe remove id and user id later?) TODO - mybe dont need to format
        safe_notes = []
        for note in user_notes:
            note_dict = dict(note)
            note_dict["created_at"] = datetime.datetime.fromisoformat(note_dict["created_at"]).strftime("%d/%m/%Y")
            safe_notes.append(note_dict)

        return jsonify(safe_notes)

    return app
