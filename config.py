import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "audios")
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    SQLALCHEMY_DATABASE_URI = "sqlite:///users.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

