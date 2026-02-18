from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
# from .models import User
from . import db
from flaskr.db import get_db, add_user, auth_user, save_message, get_messages, get_user_notes, save_note, delete_note, get_note, update_user_note
from flaskr.helpers import login_required

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    # Forget any user_id
    session.clear()

    return render_template("login.html")

@auth.route("/login", methods=["POST"])
def login_post():

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
    # Remember which user has logged in
    session["user_id"] = user_id
           
    # Check what to return (probably redirect to home page?)
    return {"sucess": True}, 200
    
@auth.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect("/")

@auth.route("/register")
def register():
    return render_template("register.html")

@auth.route("/register", methods=["POST"])
def register_post():
    """Register user"""
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
            
    # TODO Check if email in proper email format (maybe library?)
            
    # Add user to db
    db = get_db()
    new_user =  add_user(db, email, generate_password_hash(password))
    db.commit()

    # Check if user allready exists 
    if not new_user:
        print("user exists")
        return "TODO users exists ask to login"
           
    # Check what to return (probably redirect to home page?)
    return {}, 200
