import os
import ast
import uuid
import numpy as np

from src import db
from .models import User
from .agent import Agent
from .audio_preprocessor import AudioPreprocessor

from flask import Blueprint, request, jsonify
# from dstack_sdk import AsyncTappdClient, DeriveKeyResponse, TdxQuoteResponse

api = Blueprint("api", __name__)

BASE_DIR = os.path.abspath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "audios")

API_KEY = "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"

agent = Agent(API_KEY)

PHRASES = {
    0: "I love NEAR.",
    1: "ZCash and NEAR are the best.",
    2: "I want to trade 15 NEAR to ZCash."
}


@api.route("/", methods=["GET"])
def root():
    return jsonify({"message": f"The World! Call /derivekey or /tdxquote"})


@api.route("/verify_user", methods=["GET"])
def verify_user():
    data = request.form
    if not data or "wallet_id" not in data:
        return jsonify({"error": "Missing wallet_id"}), 400

    if "audio" not in request.files:
        return jsonify({"error": "No file part"}), 400

    user = User.query.filter_by(wallet_id=data["wallet_id"]).first()

    if not user:
        return jsonify({"error": "User doesn't exist."}), 400

    file = request.files["audio"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file.filename.endswith(".wav"):
        unique_filename = f"{uuid.uuid4().hex}.wav"
        audio_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        file.save(audio_path)
    else:
        return jsonify({"error": "Invalid file format. Only .wav files are allowed"}), 401
    
    # Preprocessing audio
    AudioPreprocessor().preprocess(audio_path, audio_path)

    # Verify if the voice is from the user
    scores = agent.verify_if_voice_is_from_user(audio_path, user)

    print(scores)
    if scores[0] <= 0.5 or scores[1] <= 0.5 or scores[2] <= 0.5:
        return jsonify({"error": "The voice was not verified by biometric validation."}), 402
    
    score = agent.verify_text_recognition(audio_path, data["message"])

    if score < 0.9:
        return jsonify({"error": "The message wasn't said clear."}), 403
    
    # Confirm the operation

    # ---------------------
    return jsonify({
        "message": "succedd"
    }), 200


@api.route("/quote", methods=["POST"])
def quote():
    data = request.form
    if not data or "wallet_id" not in data:
        return jsonify({"error": "Missing wallet_id"}), 400

    if "audio" not in request.files:
        return jsonify({"error": "No file part"}), 400

    user = User.query.filter_by(wallet_id=data["wallet_id"]).first()

    if not user:
        return jsonify({"error": "User doesn't exist."}), 400

    file = request.files["audio"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file.filename.endswith(".wav"):
        unique_filename = f"{uuid.uuid4().hex}.wav"
        quote_audio_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        file.save(quote_audio_path)
    else:
        return jsonify({"error": "Invalid file format. Only .wav files are allowed"}), 401
    
    # Preprocessing audio
    AudioPreprocessor().preprocess(quote_audio_path, quote_audio_path)

    # Verify what the user wants
    sentence = agent.recognize_audio(quote_audio_path)
    print(sentence)
    informations = ast.literal_eval(agent.identifying_the_keywords(sentence))

    print(informations)

    if informations == dict():
        return jsonify({"error": "Wasn't possible to identify the params of the swap quote"}), 403

    os.remove(quote_audio_path)
    
    # Here will have the instructions to prepare the swap.

    # -----------------------

    return jsonify({
        "message": "succedd",
        "text": "I love pizza."
    }), 200


@api.route("/register", methods=["POST"])
def register_user():
    data = request.form
    if not data or "wallet_id" not in data:
        return jsonify({"error": "Missing wallet_id"}), 400

    if User.query.filter_by(wallet_id=data["wallet_id"]).first():
        return jsonify({"error": "User already exists"}), 400
    
    voice_file_1 = request.files.get("voice_file_1")
    voice_file_2 = request.files.get("voice_file_2")
    voice_file_3 = request.files.get("voice_file_3")

    voice_files = [voice_file_1, voice_file_2, voice_file_3]
    
    voice_paths = []
    for file in voice_files:
        if file and file.filename.endswith(".wav"):
            filename = f"{uuid.uuid4().hex}.wav"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            voice_paths.append(file_path)
        else:
            return jsonify({"error": "Only .wav files are allowed"}), 400
    
    preprocessor = AudioPreprocessor()
    preprocessor.preprocess_parallel([(path, path) for path in voice_paths])

    new_user = User(
        wallet_id=data["wallet_id"], 
        voiceprint1_path=voice_paths[0], 
        voiceprint2_path=voice_paths[1],
        voiceprint3_path=voice_paths[2]
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user": {"id": new_user.id, "wallet_id": new_user.wallet_id, "voiceprint_paths": voice_paths}
    }), 201
