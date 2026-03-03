from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

class ChatLog(db.Model):
    __tablename__ = "chat_log"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, 
        db.ForeignKey("users.id"),
        nullable=False
    )

    message = db.Column(db.Text, nullable=False)

    role = db.Column(db.String, nullable=False)

    created_at = db.Column(db.DateTime, default = datetime.now())

    # name optional but saves debugging time later
    # it replaces naming a constraint in sql - CONSTRAINT check_role_valid CHECK (role IN ('assistant', 'user'))
    __table_args__ = (
        db.CheckConstraint(
            "role IN ('assistant', 'user')",
            name="check_role_valid" 
        ),
    )

class UserNotes(db.Model):
    __tablename__ = "user_notes"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    note = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default = datetime.now())