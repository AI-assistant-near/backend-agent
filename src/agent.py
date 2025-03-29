import os
import re
import threading
import numpy as np
import speech_recognition as sr

from typing import Tuple
from openai import OpenAI
from dotenv import load_dotenv
from difflib import SequenceMatcher

from speechbrain.inference import SpeakerRecognition

class Agent:
    def __init__(self, api_key: str):
        # Initialize OpenAI client and speech recognizer
        # self.client = OpenAI(
        #     base_url="https://openrouter.ai/api/v1",
        #     api_key=api_key,
        # )
        self.client = OpenAI(api_key=api_key)

        self.recognizer = sr.Recognizer()
        self.speaker_rec = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb", 
            savedir="pretrained_models/speaker_rec"
        )

    def verify_vocal_biometrics(self, file1: str, file2: str) -> Tuple[float, bool]:
        # Compare two audio files to verify speaker identity

        score, prediction = self.speaker_rec.verify_files(file1, file2)
        return score, prediction

    def cleaning_sentence(self, sentence: str) -> str:
        # Clean a sentence by converting to lowercase and removing special characters
        sentence = sentence.lower().strip()
        return re.sub(r"[^\w\s]", "", sentence)

    def verify_text_recognition(self, file: str, original_sentence: str) -> float:
        # Transcribe an audio file and compare it to an expected sentence
        text = self.recognize_audio(file)

        return SequenceMatcher(
            None, 
            self.cleaning_sentence(text), 
            self.cleaning_sentence(original_sentence)
        ).ratio()

    def recognize_audio(self, file: str) -> str:
        # Convert speech from an audio file into text
        with sr.AudioFile(file) as source:
            audio = self.recognizer.record(source)
        text = self.recognizer.recognize_google(audio)
        return text

    def identifying_the_keywords(self, sentence: str) -> str:
        # Extract relevant trade information (e.g., currency exchange details) from a sentence
        prompt = f"""
            You are a helpful assistant that extracts specific information from sentences.
            If the sentence is too distant from the pattern, just return an empty string.

            Example 1:
            Sentence: "I want to trade 15 near to the cash."
            Extracted Info: {{'from': 'near', 'to': 'zcash', 'quantity': 15}}

            Example 2:
            Sentence: "I wish to exchange 20 z cash for near."
            Extracted Info: {{'from': 'zcash', 'to': 'near', 'quantity': 20}}

            Example 3:
            Sentence: "I would like to swap 5 near for cash."
            Extracted Info: {{'from': 'near', 'to': 'cash', 'quantity': 5}}

            Now, extract the information from the following sentence:
            Sentence: {sentence}
            Extracted Info:
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Respond ONLY with the extracted JSON. No reasoning, no notes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )

        message = response.choices[0].message.content
        return  "{}" if message == "" else message
    
    def execute_parallel_verification(self, quote_audio_path, compare_audio_path, dict_scores, index):
        score, _ = self.verify_vocal_biometrics(quote_audio_path, compare_audio_path)
        dict_scores[index] = np.array(score, dtype=float)[0]

    def verify_if_voice_is_from_user(self, quote_audio_path, user) -> bool:
        threads = []

        scores = {}
        for idx, voicepath in enumerate([user.voiceprint1_path, user.voiceprint2_path, user.voiceprint3_path]):
            thread = threading.Thread(
                target=self.execute_parallel_verification, 
                args=(quote_audio_path, voicepath, scores, idx)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
        
        return scores
    
    

if __name__ == "__main__":
    load_dotenv()
    agent = Agent(os.getenv("LLM_KEY"))

    print(agent.identifying_the_keywords("I want to swap 15 near to zcash"))