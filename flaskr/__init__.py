from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()
# Initialize SQLAlchemy instance 
db = SQLAlchemy()

# from https://flask.palletsprojects.com/en/stable/tutorial/factory/
def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
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

    with app.app_context():
        db.create_all()  

    # From https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
    # Register blueprints 
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app