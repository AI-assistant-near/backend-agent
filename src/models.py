from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from src import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(80), unique=True, nullable=False)
    private_key = db.Column(db.String(100), unique=True, nullable=False)
    public_key = db.Column(db.String(100), unique=True, nullable=False)
    voiceprint1_path = db.Column(db.String(255), nullable=True)
    voiceprint2_path = db.Column(db.String(255), nullable=True)
    voiceprint3_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())