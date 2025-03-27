import re
import speech_recognition as sr
from typing import Tuple
from openai import OpenAI
from difflib import SequenceMatcher
from speechbrain.inference import SpeakerRecognition

class Agent:
    def __init__(self, api_key: str):
        # Initialize OpenAI client and speech recognizer
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.recognizer = sr.Recognizer()

    def verify_vocal_biometrics(self, file1: str, file2: str) -> Tuple[float, bool]:
        # Compare two audio files to verify speaker identity
        speaker_rec = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb", 
            savedir="tmpdir"
        )
        score, prediction = speaker_rec.verify_files(file1, file2)
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
            If the sentence is too distant from the pattern, just return "I can't identify."

            Example 1:
            Sentence: "I want to trade 15 near to btc."
            Extracted Info: {{'from': 'near', 'to': 'btc', 'quantity': 15}}

            Example 2:
            Sentence: "I wish to exchange 20 btc for near."
            Extracted Info: {{'from': 'btc', 'to': 'near', 'quantity': 20}}

            Example 3:
            Sentence: "I would like to swap 5 near for btc."
            Extracted Info: {{'from': 'near', 'to': 'btc', 'quantity': 5}}

            Now, extract the information from the following sentence:
            Sentence: {sentence}
            Extracted Info:
        """
        
        response = self.client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=[
                {"role": "system", "content": "Respond ONLY with the extracted JSON. No reasoning, no notes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )
        return response.choices[0].message.content