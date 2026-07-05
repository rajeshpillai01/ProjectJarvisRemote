import pyttsx3
import threading
from pydantic import BaseModel, Field

class SpeakArgs(BaseModel):
    phrase: str = Field(description="The strict textual phrase Jarvis should speak out loud from the host PC speakers.")

def speak_out_loud(phrase: str) -> str:
    """Uses the physical Windows speech synthesis engine to output vocal audio into the local environment."""
    def worker():
        engine = pyttsx3.init()
        # Set rate and voice properties cleanly
        engine.setProperty('rate', 175)
        voices = engine.getProperty('voices')
        # Standard default configuration selects a clean masculine/feminine native desktop voice
        if len(voices) > 0:
            engine.setProperty('voice', voices[0].id)
        engine.say(phrase)
        engine.runAndWait()

    # Run inside a separate background worker thread to ensure the Telegram client loop never hitches or lags
    threading.Thread(target=worker, daemon=True).start()
    return f"Vocalizing phrase locally: '{phrase}'"