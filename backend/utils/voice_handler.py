import speech_recognition as sr
from typing import Callable, Dict

class VoiceHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def adjust_for_ambient_noise(self, source):
        self.recognizer.adjust_for_ambient_noise(source)
        
    def listen_for_command(self, source, timeout=1):
        try:
            audio = self.recognizer.listen(source, timeout=timeout)
            return self.recognizer.recognize_google(audio).lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None