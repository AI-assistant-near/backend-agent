import os
import ast
import uuid
import numpy as np

from src import db
from .models import User
from .agent import Agent

from flask import Blueprint, request, jsonify
from dstack_sdk import AsyncTappdClient, DeriveKeyResponse, TdxQuoteResponse

api = Blueprint("api", __name__)

BASE_DIR = os.path.abspath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "audios")

API_KEY = ""

agent = Agent(API_KEY)

@api.route("/", methods=["GET"])
def root():
    score = agent.verify_vocal_biometrics("audios/0fbbbd3d0bde3d8f34e4b86a5fc7ff4b.wav", "audios/69bad19929154ebc22a64c647e7806fd.wav")
    return jsonify({"message": f"The World! Call /derivekey or /tdxquote {str(score)}"})


@api.route("/command", methods=["POST"])
def command():
    data = request.form
    if not data or "username" not in data:
        return jsonify({"error": "Missing username"}), 400

    if "audio" not in request.files:
        return jsonify({"error": "No file part"}), 400

    user = User.query.filter_by(username=data["username"]).first()

    if not user:
        return jsonify({"error": "User doesn't exist."}), 400

    file = request.files["audio"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file.filename.endswith(".wav"):
        unique_filename = f"{uuid.uuid4().hex}.wav"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        file.save(file_path)
    else:
        return jsonify({"error": "Invalid file format. Only .wav files are allowed"}), 400
    
    # Verify if the voice is from the suer
    score1, pred = agent.verify_vocal_biometrics(file_path, user.voiceprint1_path)
    score2, pred = agent.verify_vocal_biometrics(file_path, user.voiceprint2_path)

    if score1 <= 0.45 or score2 <= 0.45:
        return jsonify({"error": "The voice was not verified by biometric validation."}), 400

    # Verify what the user wants
    sentence = agent.recognize_audio(file_path)
    informations = ast.literal_eval(agent.identifying_the_keywords(sentence))

    os.remove(file_path)

    # Here will have the instructions to execute the command.

    return jsonify({
        "message": "succeed!"
    }), 200


@api.route("/register", methods=["POST"])
def register_user():
    data = request.form
    if not data or "username" not in data:
        return jsonify({"error": "Missing username"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "User already exists"}), 400
    
    voice_file_1 = request.files.get("voice_file_1")
    voice_file_2 = request.files.get("voice_file_2")

    voice_files = [voice_file_1, voice_file_2]
    
    voice_paths = []
    for file in voice_files:
        if file and file.filename.endswith(".wav"):
            filename = f"{uuid.uuid4().hex}.wav"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            voice_paths.append(file_path)
        else:
            return jsonify({"error": "Only .wav files are allowed"}), 400

    new_user = User(username=data["username"], voiceprint1_path=voice_paths[0], voiceprint2_path=voice_paths[1])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user": {"id": new_user.id, "username": new_user.username, "voiceprint_paths": voice_paths}
    }), 201
