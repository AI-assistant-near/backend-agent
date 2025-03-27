from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from src import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # email = db.Column(db.String(120), unique=True, nullable=False)
    voiceprint1_path = db.Column(db.String(255), nullable=True)
    voiceprint2_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())