import os
import threading
import numpy as np
import noisereduce as nr

from pydub import AudioSegment, silence


class AudioPreprocessor:
    def __init__(self, silence_thresh=-40, noise_reduce=True):
        self.silence_thresh = silence_thresh
        self.noise_reduce = noise_reduce

    def preprocess(self, file_path, output_path):
        # Load audio file
        audio = AudioSegment.from_wav(file_path)
        
        # Trim silence
        trimmed_audio = self.trim_silence(audio)
        
        # Convert to numpy array for noise reduction
        if self.noise_reduce:
            trimmed_audio = self.reduce_noise(trimmed_audio)
        
        # Save processed audio
        trimmed_audio.export(output_path, format="wav")

    def trim_silence(self, audio):
        non_silent_chunks = silence.split_on_silence(
            audio, 
            silence_thresh=self.silence_thresh,
            keep_silence=100  # Keeps a small part of silence for natural transitions
        )
        return sum(non_silent_chunks, AudioSegment.empty())

    def reduce_noise(self, audio):
        samples = np.array(audio.get_array_of_samples()).astype(np.float32)
        sample_rate = audio.frame_rate
        
        # Apply noise reduction
        reduced_noise = nr.reduce_noise(y=samples, sr=sample_rate, prop_decrease=0.8)
        
        # Convert back to AudioSegment
        return AudioSegment(
            reduced_noise.astype(np.int16).tobytes(), 
            frame_rate=sample_rate, 
            sample_width=audio.sample_width, 
            channels=audio.channels
        )
    
    def preprocess_parallel(self, input_output_pairs):
        threads = []
        for input_path, output_path in input_output_pairs:
            thread = threading.Thread(target=self.preprocess, args=(input_path, output_path))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()

# Example usage:
if __name__ == "__main__":
    processor = AudioPreprocessor()
    processor.preprocess("t.wav", "t.wav")
