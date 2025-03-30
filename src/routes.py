import os
import ast
import uuid
import asyncio
import numpy as np
import near_api

from py_near.account import Account

from src import db
from .models import User
from .agent import Agent
from .audio_preprocessor import AudioPreprocessor
from .near_utils import get_quote, create_new_near_account, RPC_URL, deposit_near, execute_intent, create_new_zcash_account, register_pub_key, register_near_storage, withdraw_zcash
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

    if not data or "account_id" not in data or "quote" not in data:
        return jsonify({"error": "Missing account_id or quote"}), 400

    if "audio" not in request.files:
        return jsonify({"error": "No file part"}), 400

    quote = data["quote"]
    user = User.query.filter_by(account_id=data["account_id"]).first()

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
    
    score = agent.verify_text_recognition(audio_path, data["text"])

    if score < 0.63:
        return jsonify({"error": "The text wasn't said clear."}), 403
    
    # Confirm the operation
    key_pair = near_api.signer.KeyPair(user.private_key)
    signer = near_api.signer.Signer(user.account_id, key_pair)
    
    account = Account(account_id=user.account_id, private_key=user.private_key, rpc_addr=RPC_URL)
    asyncio.run(account.startup())

    asyncio.run(register_pub_key(account, user.public_key_near))
    asyncio.run(register_near_storage(account))

    if data["near_to_zcash"]:
        # Deposit NEAR
        print("Depositing NEAR...")
        asyncio.run(deposit_near(account, data["amount_in"]))
        print("Deposit successful")

    result = asyncio.run(execute_intent(user.account_id, signer, quote))
    print("Intent execution result:", result)

    asyncio.run(asyncio.sleep(20))

    print("Withdrawing ZEC...")
    result = asyncio.run(withdraw_zcash(
        account_id=user.account_id,
        signer=signer,
        amount=float(quote['amount_out']) / 10**8, 
        zcash_address=user.address_zcash
    ))
    print("Withdrawal intent submitted:", result)
    
    return jsonify({
        "zcash_url": f"https://mainnet.zcashexplorer.app/address/{user.address_zcash}"
    }), 200


@api.route("/api/command", methods=["POST"])
def command():
    data = request.form
    if not data or "account_id" not in data:
        return jsonify({"error": "Missing account_id"}), 400

    if "audio" not in request.files:
        return jsonify({"error": "No file part"}), 400

    user = User.query.filter_by(account_id=data["account_id"]).first()

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
    quote = get_quote(informations["quantity"], informations["from"] == "near")
    # -----------------------

    return jsonify({
        "text": generate_random_sentence_with_nouns(),
        # "amount_in": quote["amount_in"] / (10**24),
        # "near_to_zcash": informations["from"] == "near",
        # "amount_out": quote["amount_out"] / (10**8),
        # "expiration_time": quote["expiration_time"],
        "quote": quote
    }), 200


@api.route("/api/register", methods=["POST"])
def register_user():
    data = request.form
    
    voice_file_1 = request.files.get("voice_file_0")
    voice_file_2 = request.files.get("voice_file_1")
    voice_file_3 = request.files.get("voice_file_2")

    voice_files = [voice_file_1, voice_file_2, voice_file_3]
    
    voice_paths = []
    preprocessor = AudioPreprocessor()

    for file in voice_files:
        if file and file.filename.endswith(".wav"):
            filename = f"{uuid.uuid4().hex}.wav"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            voice_paths.append(file_path)
        else:
            return jsonify({"error": "Only .wav files are allowed"}), 400
    
    preprocessor.preprocess_parallel([(path, path) for path in voice_paths])

    username = agent.recognize_audio(voice_paths[2]).replace(" ", "-").lower()
    # username = "antonio"
    account_id = username + ".zcash-sponsor.near"

    user = User.query.filter_by(account_id=account_id).first()
    if user:
        return jsonify({
            "message": "User already exists",
            "user": {"id": user.id, "account_id": user.account_id}
        })

    new_account_private_key_near, near_public_key_near = asyncio.run(create_new_near_account(account_id, 0))
    new_account_private_key_zcash, address = asyncio.run(create_new_zcash_account())

    new_user = User(
        account_id=account_id, 
        private_key_near=new_account_private_key_near,
        public_key_near=near_public_key_near,
        private_key_zcash=new_account_private_key_zcash,
        address_zcash=address,
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