from flask import Flask, render_template, request, url_for, g, session, redirect
from flask_session import Session
import os

from flaskr.db import get_db, add_user, auth_user
from flaskr.helpers import login_required


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

    # Check if placement good here 
    from . import db
    db.init_app(app)

    ### Template and API routes ###

    @app.route("/")
    @login_required
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
        
    @app.route("/logout")
    def logout():
        """Log user out"""

        session.clear()

        return redirect("/")
        
    @app.route("/registar", methods=["GET", "POST"])
    def registar():
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


    return app

# https://flask.palletsprojects.com/en/stable/quickstart/#variable-rules - use this for user note edit mode?
# https://flask.palletsprojects.com/en/stable/quickstart/#http-methods - can separate app.post and app.get requests like so
