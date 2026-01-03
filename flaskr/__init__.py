from flask import Flask, render_template, request, url_for, g, session, redirect, current_app, jsonify
from flask_session import Session
import os
from dotenv import load_dotenv
import datetime
from collections import defaultdict

from flaskr.db import get_db, add_user, auth_user, save_message, get_messages
from flaskr.helpers import login_required

from groq import Groq

# from https://flask.palletsprojects.com/en/stable/tutorial/factory/
def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'database.db'),
        SESSION_PERMANENT = False,
        SESSION_TYPE = "filesystem"
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

    Session(app)
    load_dotenv()

    # Check if placement good here 
    from . import db
    db.init_app(app)

    ### Template and API routes ###
    @app.route("/")
    def index():
        print(url_for('index'))
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Log user in"""

        # Forget any user_id
        session.clear()
    
        if request.method == "GET":
            return render_template("login.html")
        
        if request.method == "POST":

            #Add try catch block 
            data = request.get_json()

            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                print("need to fill all fields")
                return "TODO handle error"
              
            # Authenticate user 
            user = auth_user(email, password)
            
            if not user: 
                print("user does not exist")
                return "TODO user does not exist"
            
            user_id =  user["id"]
            print(user_id)
            # Remember which user has logged in
            session["user_id"] = user_id
           
            # Check what to return (probably redirect to home page?)
            return {"sucess": True}, 200


    @app.route("/test")
    def test():
        return "OK"
    
    @app.route("/assistant")
    @login_required
    def assistant():

        return render_template("assistant.html")

    
    @app.route("/api/send_message", methods=["POST"])
    @login_required
    def send_message():
        # From https://console.groq.com/docs/quickstart
        api_key = os.getenv("GROQ_API_KEY")
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
           return "TODO error with wrting message to bd"
        
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

    @app.route("/logout")
    def logout():
        """Log user out"""

        session.clear()

        return redirect("/")
        
    @app.route("/register", methods=["GET", "POST"])
    def register():
        """Register user"""

        if request.method == "GET":
            return render_template("register.html")
        
        if request.method == "POST":

            #Add try catch block 
            data = request.get_json()

            email = data.get("email")
            password = data.get("password")
            password_confirm = data.get("password_confirm")

            if not email or not password or not password_confirm:
                print("need to fill all fields")
                return "TODO handle error"
            
            if password != password_confirm:
                print("pasword mismatch")
                return "TODO handle error"
            
            # TODO Check if email in proper email format (maybe in js?)
            
            # Add user to db
            db = get_db()
            user_id =  add_user(db, email, password)
            db.commit()
            # Check if user allready exists 
            if not user_id:
                print("user exists")
                return "TODO users exists ask to login"
           
            # Check what to return (probably redirect to home page?)
            return {}, 200

    @app.route("/history")
    @login_required
    def chat_history():
        user_id = session.get("user_id")
        # formating messages by date 
        # from https://docs.python.org/3/library/collections.html#defaultdict-examples
        sorted_messages = defaultdict(list) # Order not guarenteed need to fix later 

        for msg in get_messages(user_id):
            # https://note.nkmk.me/en/python-datetime-isoformat-fromisoformat/
            date = datetime.datetime.fromisoformat(msg["created_at"]).date()
            sorted_messages[date].append(msg)

        return render_template("history.html", messages=sorted_messages)

    return app

# https://flask.palletsprojects.com/en/stable/quickstart/#variable-rules - use this for user note edit mode?
# https://flask.palletsprojects.com/en/stable/quickstart/#http-methods - can separate app.post and app.get requests like so
