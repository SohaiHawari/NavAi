"""
NavAI - Speech Processing Module
Handles Speech-to-Text (STT) and Text-to-Speech (TTS) for desktop testing.
Note: On mobile, React Native handles STT/TTS natively.
"""

import logging
import platform

logger = logging.getLogger("NavAI.Speech")


class SpeechToText:
    """
    Speech-to-Text engine using Google Speech Recognition.
    Used for desktop testing; mobile app uses native STT.
    """

    def __init__(self, language: str = "en-US"):
        """
        Initialize STT engine.

        Args:
            language: Recognition language code
        """
        import speech_recognition as sr

        self.recognizer = sr.Recognizer()
        self.language = language
        logger.info(f"STT initialized for language: {language}")

    def listen_and_convert(self) -> str:
        """
        Listen to microphone and convert speech to text.

        Returns:
            Recognized text string
        """
        import speech_recognition as sr

        with sr.Microphone() as source:
            logger.info("🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)

        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.info(f"📝 Recognized: {text}")
            return text
        except Exception as e:
            logger.error(f"STT failed: {e}")
            return ""

    def convert_audio_file(self, audio_path: str) -> str:
        """
        Convert an audio file to text.

        Args:
            audio_path: Path to audio file (WAV format)

        Returns:
            Recognized text string
        """
        import speech_recognition as sr

        with sr.AudioFile(audio_path) as source:
            audio = self.recognizer.record(source)

        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
        except Exception as e:
            logger.error(f"Audio STT failed: {e}")
            return ""


class TextToSpeech:
    """
    Text-to-Speech engine using pyttsx3.
    Used for desktop testing; mobile app uses native TTS.
    """

    def __init__(self, rate: int = 150, volume: float = 1.0):
        """
        Initialize TTS engine.

        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
        """
        import pyttsx3

        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)

        # Set voice (prefer female voice for assistant feel)
        voices = self.engine.getProperty("voices")
        if len(voices) > 1:
            self.engine.setProperty("voice", voices[1].id)  # Usually female

        logger.info("TTS initialized")

    def speak(self, text: str):
        """
        Convert text to speech and play it.

        Args:
            text: Text to speak
        """
        logger.info(f"🔊 Speaking: {text[:50]}...")
        self.engine.say(text)
        self.engine.runAndWait()

    def save_to_file(self, text: str, output_path: str):
        """
        Save speech to an audio file.

        Args:
            text: Text to convert
            output_path: Path for output audio file
        """
        self.engine.save_to_file(text, output_path)
        self.engine.runAndWait()
        logger.info(f"Audio saved to: {output_path}")
