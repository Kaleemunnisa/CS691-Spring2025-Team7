from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100))  # or use Flask-Login user id
    mood = db.Column(db.Integer)
    session_completed = db.Column(db.Integer)
    sleep = db.Column(db.Integer)
    energy = db.Column(db.Integer)
    focus = db.Column(db.Integer)
    stress = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=db.func.now())
