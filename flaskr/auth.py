from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flaskr.db import auth_user
import re

auth = Blueprint('auth', __name__)

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    
    if not user: 
        return None
    
    if not check_password_hash(user.password_hash, password):
        return None

    return user

@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route("/login", methods=["POST"])
def login_post():
    """Login user"""
    data = request.get_json()
    if not data:
        return {"ok": False, "error": "Invalid or missing JSON"}, 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"ok": False, "error": "All fields are required"}
       
    user = authenticate_user(email, password)
            
    if not user: 
        return {"ok": False, "error": "Invalid credentials"}
            
    user_id =  user.id
    # Remember which user has logged in
    session["user_id"] = user_id
           
    return {"ok": True, "message": "Login successful"}, 201
    
@auth.route("/logout")
def logout():
    """Log user out"""
    session.clear()

    return {"ok": True, "message": "Logout successful"}, 201


def register_user(email, password_hash):
    existing = User.query.filter_by(email=email).first()
    if existing:
        return None
    
    # create new user
    user = User(email, password_hash)
    
    # add the new user to the database 
    db.session.add(user)
    db.session.commit()

    return user

@auth.route("/register")
def register():
    return render_template("register.html")

@auth.route("/api/register", methods=["POST"])
def register_post():
    """Register user"""
    data = request.get_json(silent=True)
    if not data:
        return {"ok": False, "error": "Invalid or missing JSON"}, 400

    email = data.get("email")
    password = data.get("password")
    password_confirm = data.get("password_confirm")

    if not email or not password or not password_confirm:
        return {"ok": False, "error": "All fields are required"}, 400
    
    # https://www.geeksforgeeks.org/python/check-if-email-address-valid-or-not-in-python/
    regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"
    if not re.fullmatch(regex, email): 
        return {"ok": False, "error": "Invalid email"}, 400
    
    if password != password_confirm:
        return {"ok": False, "error": "Password mismatch"}, 400
    
    password_hash = generate_password_hash(password)

    # add user to db
    user = register_user(email, password_hash)
    # check if email exists in the db
    if not user:
        return {"ok": False, "error": "User already exists"}, 400
            
    return {"ok": True, "message": "User created"}, 201
