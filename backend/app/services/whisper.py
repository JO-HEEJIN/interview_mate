"""
OpenAI Whisper API integration for speech-to-text
"""

import io
import logging
import tempfile
from openai import OpenAI
from app.core.config import settings

# 로거 설정
logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        logger.info("Whisper service initialized")

    def _detect_audio_format(self, audio_data: bytes) -> str:
        """
        Detect audio format from file header.

        Returns file extension (.webm, .ogg, .mp4, etc.)
        """
        if len(audio_data) < 12:
            logger.warning("Audio data too short to detect format, defaulting to .webm")
            return '.webm'

        header = audio_data[:12]

        # WebM: starts with 0x1A45DFA3 (EBML header)
        if header[:4] == b'\x1A\x45\xDF\xA3':
            return '.webm'

        # Ogg: starts with "OggS"
        if header[:4] == b'OggS':
            return '.ogg'

        # MP4/M4A: has 'ftyp' at bytes 4-8
        if header[4:8] == b'ftyp':
            return '.m4a'

        # WAV: starts with "RIFF" and has "WAVE"
        if header[:4] == b'RIFF' and audio_data[8:12] == b'WAVE':
            return '.wav'

        # MP3: starts with ID3 or 0xFF (sync word)
        if header[:3] == b'ID3' or header[0] == 0xFF:
            return '.mp3'

        # Default to webm if unknown
        logger.warning(f"Unknown audio format, header: {header.hex()}, defaulting to .webm")
        return '.webm'

    async def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        """
        Transcribe audio data to text using Whisper API.

        Args:
            audio_data: Raw audio bytes (webm format from browser)
            language: Language code (default: English)

        Returns:
            Transcribed text
        """
        if not audio_data:
            logger.warning("Empty audio data received")
            return ""

        try:
            logger.info(f"Transcribing audio data: {len(audio_data)} bytes, language: {language}")

            # Check audio data header to determine format
            audio_header = audio_data[:12] if len(audio_data) >= 12 else audio_data
            logger.debug(f"Audio header: {audio_header.hex()}")

            # Detect file format from header
            file_extension = self._detect_audio_format(audio_data)
            logger.info(f"Detected audio format: {file_extension}")

            # Create a temporary file with the correct extension
            with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file.flush()
                temp_file_path = temp_file.name

            try:
                # Interview-specific prompt to guide transcription
                prompt = (
                    "This is an interview recording. "
                    "Transcribe clear interview questions accurately. "
                    "Ignore filler words, repetitions, and incomplete thoughts. "
                    "Focus on complete questions only."
                )

                with open(temp_file_path, 'rb') as audio_file:
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

            finally:
                # Clean up temporary file
                import os
                try:
                    os.unlink(temp_file_path)
                except Exception as cleanup_err:
                    logger.warning(f"Failed to delete temp file: {cleanup_err}")

        except Exception as e:
            logger.error(f"Whisper transcription error: {str(e)}", exc_info=True)

            # If webm fails, log more details
            if "Invalid file format" in str(e):
                logger.error(f"Audio format detection failed. Data size: {len(audio_data)}, Header: {audio_data[:20].hex() if len(audio_data) >= 20 else 'too short'}")

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
