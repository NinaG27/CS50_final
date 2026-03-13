from flask import Blueprint, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
import re

auth = Blueprint("auth", __name__)


def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()

    if not user:
        return None

    if not check_password_hash(user.password_hash, password):
        return None

    return user


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/api/login", methods=["POST"])
def login_post():
    """Login user"""
    data = request.get_json()
    if not data:
        return {"error": "Invalid or missing JSON"}, 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"error": "All fields are required"}, 400

    user = authenticate_user(email, password)
    if not user:
        return {"error": "Invalid credentials"}, 400

    user_id = user.id
    # Remember which user has logged in
    session["user_id"] = user_id

    return {"message": "Login successful"}, 201


@auth.route("/logout")
def logout():
    """Log user out"""
    session.clear()

    return {"message": "Logout successful"}, 201


def register_user(email, password_hash):
    existing = User.query.filter_by(email=email).first()
    if existing:
        return None

    # create new user
    user = User(email=email, password_hash=password_hash)

    try:
        # add the new user to the database
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Error registering user", e)
        return None

    return user


@auth.route("/register")
def register():
    return render_template("register.html")


@auth.route("/api/register", methods=["POST"])
def register_post():
    """Register user"""
    data = request.get_json(silent=True)
    if not data:
        return {"error": "Invalid or missing JSON"}, 400

    email = data.get("email")
    password = data.get("password")
    password_confirm = data.get("password_confirm")

    if not email or not password or not password_confirm:
        return {"error": "All fields are required"}, 400

    # https://www.geeksforgeeks.org/python/check-if-email-address-valid-or-not-in-python/
    regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"
    if not re.fullmatch(regex, email):
        return {"error": "Invalid email"}, 400

    if password != password_confirm:
        return {"error": "Password mismatch"}, 400

    password_hash = generate_password_hash(password)

    # add user to db
    user = register_user(email, password_hash)
    # check if email exists in the db
    if not user:
        return {"error": "User already exists"}, 400

    return {"message": "User created"}, 201
