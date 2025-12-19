"""
Transcription service abstraction layer
Allows switching between Whisper and Deepgram based on configuration
"""

import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class TranscriptionService:
    """
    Factory pattern for transcription service selection.
    Supports easy switching between Whisper and Deepgram via configuration.
    """

    def __init__(self):
        self._service = None
        self._service_name = getattr(settings, 'TRANSCRIPTION_SERVICE', 'deepgram').lower()
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the appropriate transcription service based on configuration."""
        if self._service_name == 'deepgram':
            try:
                from app.services.deepgram_service import deepgram_service
                self._service = deepgram_service
                logger.info("Using Deepgram Nova-3 for transcription")
            except Exception as e:
                logger.error(f"Failed to initialize Deepgram service: {e}")
                logger.info("Falling back to Whisper")
                self._service_name = 'whisper'
                self._initialize_whisper()
        else:
            self._initialize_whisper()

    def _initialize_whisper(self):
        """Initialize Whisper service as fallback."""
        try:
            from app.services.whisper import whisper_service
            self._service = whisper_service
            logger.info("Using OpenAI Whisper for transcription")
        except Exception as e:
            logger.error(f"Failed to initialize Whisper service: {e}", exc_info=True)
            raise RuntimeError("No transcription service available")

    async def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        """
        Transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes
            language: Language code (default: English)

        Returns:
            Transcribed text
        """
        if not self._service:
            logger.error("No transcription service initialized")
            return ""

        try:
            return await self._service.transcribe(audio_data, language)
        except Exception as e:
            logger.error(f"Transcription error with {self._service_name}: {str(e)}", exc_info=True)

            # Attempt fallback to Whisper if Deepgram fails
            if self._service_name == 'deepgram':
                logger.info("Attempting fallback to Whisper")
                try:
                    self._initialize_whisper()
                    return await self._service.transcribe(audio_data, language)
                except Exception as fallback_error:
                    logger.error(f"Fallback to Whisper also failed: {fallback_error}")

            return ""

    @property
    def service_name(self) -> str:
        """Get the name of the current transcription service."""
        return self._service_name


# Global instance
transcription_service = TranscriptionService()
