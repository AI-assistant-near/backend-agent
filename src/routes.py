import os
import ast
import uuid
import asyncio
import numpy as np

from src import db
from .models import User
from .agent import Agent
from .audio_preprocessor import AudioPreprocessor
from .near_utils import get_quote, create_new_near_account
from .utils import generate_random_sentence_with_nouns

from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
# from dstack_sdk import AsyncTappdClient, DeriveKeyResponse, TdxQuoteResponse

load_dotenv()

api = Blueprint("api", __name__)

BASE_DIR = os.path.abspath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "audios")

LLM_KEY = os.getenv("LLM_KEY")

agent = Agent(LLM_KEY)

@api.route("/", methods=["GET"])
def root():
    return jsonify({"message": f"The World! Call /derivekey or /tdxquote"})

@api.route("/api/get_sample_of_quote", methods=["GET"])
def get_sample_of_quote():
    print(asyncio.run(get_quote(0.01, True)))
    return jsonify({})

@api.route("/api/verify_user", methods=["GET"])
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


@api.route("/api/command", methods=["POST"])
def command():
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
        command_audio_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        file.save(command_audio_path)
    else:
        return jsonify({"error": "Invalid file format. Only .wav files are allowed"}), 401
    
    # Preprocessing audio
    AudioPreprocessor().preprocess(command_audio_path, command_audio_path)

    # Verify what the user wants
    sentence = agent.recognize_audio(command_audio_path)
    print(sentence)
    informations = ast.literal_eval(agent.identifying_the_keywords(sentence))

    print(informations)

    if informations == dict() or informations.get("quantity") == None or informations.get("from") == None or informations.get("to") == None:
        return jsonify({"error": "Wasn't possible to identify the params of the swap command"}), 403
    
    os.remove(command_audio_path)
    
    # Here will have the instructions to prepare the swap.
    # quote = get_quote(informations["quantity"], informations["from"] == "near")
    # -----------------------

    return jsonify({
        "text": generate_random_sentence_with_nouns(),
        "informations": informations
    }), 200


@api.route("/api/register", methods=["POST"])
def register_user():
    data = request.form
    
    voice_file_1 = request.files.get("voice_file_0")
    voice_file_2 = request.files.get("voice_file_1")
    voice_file_3 = request.files.get("voice_file_2")

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

    username = agent.recognize_audio(voice_paths[2]).replace(" ", "-").lower()

    account_id = username + ".zcash-sponsor.near"

    new_account_private_key, near_public_key = asyncio.run(create_new_near_account(account_id, 0))

    new_user = User(
        account_id=account_id, 
        private_key=new_account_private_key,
        public_key=near_public_key,
        voiceprint1_path=voice_paths[0], 
        voiceprint2_path=voice_paths[1],
        voiceprint3_path=voice_paths[2]
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user": {"id": new_user.id, "account_id": new_user.account_id}
    }), 201