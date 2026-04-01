from TTS.api import TTS
import threading
import tempfile
import os
import subprocess


class TTSEngine:

    def __init__(self):
        # Load XTTS model (natural sounding)
        self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

    def speak_async(self, text):
        threading.Thread(target=self._speak, args=(text,), daemon=True).start()

    def _speak(self, text):

        # Create temporary wav file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
            wav_path = fp.name

        # Generate speech
        self.tts.tts_to_file(text=text, file_path=wav_path)

        # Play audio (Linux)
        subprocess.run(["aplay", wav_path])

        # Remove file
        os.remove(wav_path)