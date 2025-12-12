"""
OpenAI Whisper API integration for speech-to-text
"""

import io
import logging
from openai import OpenAI
from app.core.config import settings

# 로거 설정
logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("Whisper service initialized")

    async def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        """
        Transcribe audio data to text using Whisper API.

        Args:
            audio_data: Raw audio bytes (WAV format preferred)
            language: Language code (default: English)

        Returns:
            Transcribed text
        """
        if not audio_data:
            logger.warning("Empty audio data received")
            return ""

        try:
            logger.info(f"Transcribing audio data: {len(audio_data)} bytes, language: {language}")

            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.webm"

            # Interview-specific prompt to guide transcription
            prompt = (
                "This is an interview recording. "
                "Transcribe clear interview questions accurately. "
                "Ignore filler words, repetitions, and incomplete thoughts. "
                "Focus on complete questions only."
            )

            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="text",
                prompt=prompt,
                temperature=0.1  # Lower temperature for more deterministic output
            )

            result = response.strip()
            logger.info(f"Transcription successful: '{result}'")
            return result

        except Exception as e:
            logger.error(f"Whisper transcription error: {str(e)}", exc_info=True)
            return ""

    async def transcribe_with_timestamps(self, audio_data: bytes, language: str = "en") -> dict:
        """
        Transcribe audio with word-level timestamps.
        """
        if not audio_data:
            logger.warning("Empty audio data received for timestamp transcription")
            return {"text": "", "words": []}

        try:
            logger.info(f"Transcribing with timestamps: {len(audio_data)} bytes")
            
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"

            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["word"]
            )

            result = {
                "text": response.text,
                "words": response.words if hasattr(response, 'words') else []
            }
            logger.info(f"Timestamp transcription successful: {len(result['text'])} chars")
            return result
            
        except Exception as e:
            logger.error(f"Whisper timestamp transcription error: {str(e)}", exc_info=True)
            return {"text": "", "words": []}


whisper_service = WhisperService()
