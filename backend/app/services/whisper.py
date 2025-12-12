"""
OpenAI Whisper API integration for speech-to-text
"""

import io
import logging
import tempfile
import subprocess
from pathlib import Path
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

    def _convert_to_wav(self, input_path: str, output_path: str) -> bool:
        """
        Convert audio to WAV using ffmpeg.

        Returns True if successful, False otherwise.
        """
        try:
            # Use ffmpeg to convert to WAV (16kHz, mono, 16-bit PCM)
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',      # Mono
                '-f', 'wav',     # WAV format
                '-y',            # Overwrite output
                output_path
            ]

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("Audio converted to WAV successfully")
                return True
            else:
                logger.error(f"FFmpeg conversion failed: {result.stderr.decode()}")
                return False

        except FileNotFoundError:
            logger.error("FFmpeg not found. Please install: brew install ffmpeg")
            return False
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg conversion timeout")
            return False
        except Exception as e:
            logger.error(f"Error converting audio: {str(e)}")
            return False

    async def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        """
        Transcribe audio data to text using Whisper API.

        Args:
            audio_data: Raw audio bytes (webm chunks from browser)
            language: Language code (default: English)

        Returns:
            Transcribed text
        """
        if not audio_data:
            logger.warning("Empty audio data received")
            return ""

        # Skip very small chunks (likely incomplete)
        if len(audio_data) < 1000:
            logger.warning(f"Audio data too small ({len(audio_data)} bytes), skipping")
            return ""

        temp_input = None
        temp_output = None

        try:
            logger.info(f"Transcribing audio data: {len(audio_data)} bytes, language: {language}")

            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
                temp_input = f.name
                f.write(audio_data)

            temp_output = temp_input.replace('.webm', '.wav')

            # Convert to WAV using ffmpeg (more reliable than format detection)
            if not self._convert_to_wav(temp_input, temp_output):
                logger.error("Failed to convert audio to WAV")
                return ""

            # Verify WAV file was created
            if not Path(temp_output).exists() or Path(temp_output).stat().st_size < 100:
                logger.error("WAV file not created or too small")
                return ""

            # Interview-specific prompt to guide transcription
            prompt = (
                "This is an interview recording. "
                "Transcribe clear interview questions accurately. "
                "Ignore filler words, repetitions, and incomplete thoughts. "
                "Focus on complete questions only."
            )

            # Transcribe the WAV file
            with open(temp_output, 'rb') as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="text",
                    prompt=prompt,
                    temperature=0.1
                )

            result = response.strip()
            logger.info(f"Transcription successful: '{result}'")
            return result

        except Exception as e:
            logger.error(f"Whisper transcription error: {str(e)}", exc_info=True)
            return ""

        finally:
            # Clean up temporary files
            for temp_file in [temp_input, temp_output]:
                if temp_file and Path(temp_file).exists():
                    try:
                        Path(temp_file).unlink()
                    except Exception as e:
                        logger.warning(f"Failed to delete temp file {temp_file}: {e}")

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
