"""
Deepgram Nova-3 API integration for speech-to-text
Uses WebSocket streaming for real-time, low-latency transcription
Converts WebM/Opus audio to linear16 PCM using ffmpeg
"""

import logging
import asyncio
import subprocess
import threading
from typing import Optional, Callable
from deepgram import AsyncDeepgramClient
from deepgram.core.events import EventType
from app.core.config import settings

logger = logging.getLogger(__name__)


class DeepgramStreamingService:
    def __init__(self):
        self.client = AsyncDeepgramClient(api_key=settings.DEEPGRAM_API_KEY)
        self.model = getattr(settings, 'DEEPGRAM_MODEL', 'nova-3')
        self.connection = None
        self.is_connected = False
        self.ffmpeg_process = None
        self.converter_thread = None
        self.stderr_thread = None
        self.listening_task = None
        self.stop_converter = False

        logger.info(f"Deepgram streaming service initialized with model: {self.model}")

    def create_connection(
        self,
        on_transcript: Callable[[str, bool], None],
        on_error: Optional[Callable[[str], None]] = None
    ):
        """
        Create Deepgram WebSocket connection context manager.

        Args:
            on_transcript: Callback for transcript results (text, is_final)
            on_error: Callback for errors

        Returns:
            Async context manager for Deepgram connection
        """
        logger.info("Creating Deepgram WebSocket connection...")

        # Store callbacks
        self._on_transcript = on_transcript
        self._on_error = on_error

        # Create WebSocket connection with direct parameters (v5 API v2 endpoint)
        # v2 API uses flux models - flux-general-en is recommended for general use
        return self.client.listen.v2.connect(
            model="flux-general-en",
            encoding="linear16",
            sample_rate=16000,
            eot_threshold=0.7,  # End of turn threshold
            eot_timeout_ms=800,  # 800ms to match our utterance detection
            eager_eot_threshold=0.3,  # Early end of turn detection
        )

    def _cleanup_ffmpeg(self):
        """
        Clean up existing ffmpeg process and threads.
        Safe to call even if nothing is running.
        """
        logger.debug("🧹 Cleaning up ffmpeg process and threads...")

        # Stop converter thread
        self.stop_converter = True

        # Kill ffmpeg process if running
        if self.ffmpeg_process:
            try:
                if self.ffmpeg_process.poll() is None:  # Still running
                    logger.debug("Terminating existing ffmpeg process")
                    self.ffmpeg_process.terminate()
                    try:
                        self.ffmpeg_process.wait(timeout=1.0)
                    except subprocess.TimeoutExpired:
                        logger.warning("FFmpeg didn't terminate, killing forcefully")
                        self.ffmpeg_process.kill()
                        self.ffmpeg_process.wait()
                self.ffmpeg_process = None
            except Exception as e:
                logger.error(f"Error killing ffmpeg: {e}")
                self.ffmpeg_process = None

        # Wait for threads to stop
        if self.converter_thread and self.converter_thread.is_alive():
            logger.debug("Waiting for converter thread to stop...")
            self.converter_thread.join(timeout=2.0)

        if self.stderr_thread and self.stderr_thread.is_alive():
            logger.debug("Waiting for stderr thread to stop...")
            self.stderr_thread.join(timeout=2.0)

        self.converter_thread = None
        self.stderr_thread = None
        logger.debug("✅ FFmpeg cleanup complete")

    async def setup_connection(self, connection):
        """
        Set up event handlers for the connection and start ffmpeg converter.
        Cleans up any existing state from previous connections.

        Args:
            connection: Deepgram connection object
        """
        # CRITICAL: Clean up any existing ffmpeg process from previous connection
        self._cleanup_ffmpeg()

        self.connection = connection

        # Reset state for new session
        self.is_connected = False
        logger.info("🔄 State reset for new connection")

        # Store event loop for thread-safe async scheduling
        # Use get_running_loop() to get the actual running loop
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            # Fallback to get_event_loop() if not in async context
            self._loop = asyncio.get_event_loop()
            logger.warning("⚠️ Using get_event_loop() fallback - this might cause issues")

        # Set up event handlers
        connection.on(EventType.MESSAGE, self._handle_transcript(self._on_transcript))
        connection.on(EventType.ERROR, self._handle_error(self._on_error))
        connection.on(EventType.OPEN, lambda _: logger.info("✓ Deepgram WebSocket opened"))
        connection.on(EventType.CLOSE, lambda _: logger.info("Deepgram WebSocket closed"))

        # Start ffmpeg immediately (streaming mode handles incomplete headers gracefully)
        self._start_ffmpeg()
        logger.info("✅ FFmpeg started and ready for streaming")

        # Start listening in background task (non-blocking)
        # start_listening() is an infinite loop that processes Deepgram messages
        self.listening_task = asyncio.create_task(connection.start_listening())
        self.is_connected = True
        logger.info("✓ Deepgram WebSocket connected and listening")

    def _start_ffmpeg(self):
        """
        Start ffmpeg process and converter threads.
        Called immediately during setup_connection().
        """
        # Defensive: cleanup any zombie process
        if self.ffmpeg_process is not None:
            logger.warning("⚠️ FFmpeg process already exists, cleaning up first...")
            self._cleanup_ffmpeg()

        try:
            logger.info("🚀 Starting ffmpeg process...")
            self.ffmpeg_process = subprocess.Popen([
                "ffmpeg",
                "-loglevel", "warning",
                "-fflags", "+genpts+igndts",
                "-err_detect", "ignore_err",
                "-f", "webm",
                "-i", "pipe:0",
                "-vn",
                "-f", "s16le",
                "-ar", "16000",
                "-ac", "1",
                "-fflags", "+discardcorrupt",
                "pipe:1"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=8192)

            # Start background thread to read from ffmpeg and send to Deepgram
            self.stop_converter = False
            self.converter_thread = threading.Thread(
                target=self._ffmpeg_to_deepgram_loop,
                daemon=True
            )
            self.converter_thread.start()

            # Start thread to monitor ffmpeg stderr for errors
            self.stderr_thread = threading.Thread(
                target=self._ffmpeg_stderr_monitor,
                daemon=True
            )
            self.stderr_thread.start()

            logger.info("✅ FFmpeg process started successfully")
        except Exception as e:
            logger.error(f"❌ Failed to start ffmpeg: {e}", exc_info=True)
            raise

    def _handle_transcript(self, callback: Callable):
        """Create transcript event handler for v2 API."""
        def handler(result):
            try:
                # v2 API returns different message structure
                event = getattr(result, "event", None)
                transcript = getattr(result, "transcript", None)

                # Determine if this is a final transcript based on event type
                is_final = event == "EndOfTurn"

                if transcript and transcript.strip():
                    logger.info(f"Transcript ({'final' if is_final else 'interim'}): '{transcript}'")
                    # Schedule async callback
                    asyncio.create_task(callback(transcript, is_final))

                # Log turn events
                if event == "StartOfTurn":
                    turn_index = getattr(result, "turn_index", None)
                    logger.debug(f"--- StartOfTurn (Turn {turn_index}) ---")
                elif event == "EndOfTurn":
                    turn_index = getattr(result, "turn_index", None)
                    eot_confidence = getattr(result, "end_of_turn_confidence", None)
                    logger.debug(f"--- EndOfTurn (Turn {turn_index}, Confidence: {eot_confidence}) ---")

            except Exception as e:
                logger.error(f"Error handling transcript: {e}", exc_info=True)

        return handler

    def _handle_error(self, callback: Optional[Callable]):
        """Create error event handler."""
        def handler(error):
            logger.error(f"Deepgram error: {error}")
            if callback:
                # Schedule async callback
                asyncio.create_task(callback(str(error)))

        return handler

    def _ffmpeg_stderr_monitor(self):
        """Monitor ffmpeg stderr for errors and warnings."""
        try:
            while not self.stop_converter and self.ffmpeg_process:
                line = self.ffmpeg_process.stderr.readline()
                if not line:
                    # No more data - check if process died
                    if self.ffmpeg_process.poll() is not None:
                        logger.error(f"🔧 FFmpeg process terminated with exit code {self.ffmpeg_process.returncode}")
                    break

                error_msg = line.decode('utf-8', errors='ignore').strip()
                if error_msg:
                    # Categorize messages
                    if 'error' in error_msg.lower() or 'fatal' in error_msg.lower():
                        logger.error(f"🔧 FFmpeg ERROR: {error_msg}")
                    elif 'warning' in error_msg.lower():
                        logger.warning(f"🔧 FFmpeg WARNING: {error_msg}")
                    else:
                        logger.debug(f"🔧 FFmpeg: {error_msg}")
        except Exception as e:
            logger.error(f"Error monitoring ffmpeg stderr: {e}", exc_info=True)

    def _ffmpeg_to_deepgram_loop(self):
        """
        Background thread that reads converted audio from ffmpeg stdout
        and sends it to Deepgram.
        """
        try:
            # Read in chunks (2560 bytes = 160ms at 16kHz mono s16le)
            chunk_size = 2560
            total_sent = 0
            consecutive_timeouts = 0
            max_consecutive_timeouts = 5  # Break if 5 timeouts in a row

            logger.info("🔄 FFmpeg converter loop started")

            while not self.stop_converter and self.ffmpeg_process:
                try:
                    # Check if ffmpeg is still alive
                    if self.ffmpeg_process.poll() is not None:
                        logger.error(f"❌ FFmpeg died in converter loop (exit code: {self.ffmpeg_process.returncode})")
                        break

                    data = self.ffmpeg_process.stdout.read(chunk_size)
                    if not data:
                        logger.info("📭 No more data from ffmpeg stdout")
                        break

                    total_sent += len(data)
                    logger.debug(f"📤 Read {len(data)} bytes from ffmpeg (total: {total_sent})")

                    # Send converted PCM data to Deepgram
                    # send_media() is async but we're in a sync thread, so schedule it
                    if self.connection and self.is_connected:
                        # Retry logic: try up to 3 times with exponential backoff
                        max_retries = 3
                        retry_delay = 0.1  # Start with 100ms

                        for attempt in range(max_retries):
                            try:
                                future = asyncio.run_coroutine_threadsafe(
                                    self.connection.send_media(data),
                                    self._loop
                                )
                                # Wait with longer timeout to handle network latency
                                # Increased from 0.5s to 2.0s, then to 5.0s for long questions
                                future.result(timeout=5.0)
                                logger.debug(f"✅ Sent {len(data)} bytes to Deepgram")
                                consecutive_timeouts = 0  # Reset counter on success
                                break  # Success - exit retry loop

                            except TimeoutError:
                                if attempt < max_retries - 1:
                                    # Retry with backoff
                                    logger.warning(
                                        f"⚠️ Timeout sending to Deepgram, retrying "
                                        f"(attempt {attempt + 1}/{max_retries})..."
                                    )
                                    import time
                                    time.sleep(retry_delay)
                                    retry_delay *= 2  # Exponential backoff
                                else:
                                    # Final attempt failed
                                    consecutive_timeouts += 1
                                    logger.error(
                                        f"❌ Failed to send after {max_retries} attempts. "
                                        f"Consecutive failures: [{consecutive_timeouts}/{max_consecutive_timeouts}]"
                                    )

                                    # Check connection health
                                    if not self.is_connected:
                                        logger.error("❌ Connection lost during timeout, stopping converter")
                                        break

                                    # Break if too many consecutive failures
                                    if consecutive_timeouts >= max_consecutive_timeouts:
                                        logger.error(
                                            f"❌ {max_consecutive_timeouts} consecutive failures, "
                                            "Deepgram connection unstable. Stopping converter."
                                        )
                                        break

                            except Exception as send_err:
                                logger.error(f"❌ Failed to send to Deepgram: {send_err}")
                                # Check if connection is still valid
                                if not self.is_connected:
                                    logger.error("Connection lost, stopping converter loop")
                                    break
                                # Break out of retry loop on non-timeout errors
                                break
                    else:
                        logger.warning("⚠️ Connection not ready, skipping chunk")

                except Exception as e:
                    if not self.stop_converter:
                        logger.error(f"❌ Error in converter loop: {e}", exc_info=True)
                    break

        except Exception as e:
            logger.error(f"❌ FFmpeg converter thread error: {e}", exc_info=True)
        finally:
            logger.info(f"🛑 FFmpeg converter thread stopped (sent {total_sent} bytes total)")

    async def send_audio(self, audio_data: bytes):
        """
        Send audio chunk to ffmpeg for conversion, which will then forward to Deepgram.

        Args:
            audio_data: Raw audio bytes (WebM/Opus format from client)
        """
        if not self.ffmpeg_process or not self.ffmpeg_process.stdin:
            logger.warning("⚠️ Cannot send audio: ffmpeg not started")
            return False

        # Check if ffmpeg process is still alive
        if self.ffmpeg_process.poll() is not None:
            exit_code = self.ffmpeg_process.returncode
            logger.error(f"❌ FFmpeg process died with exit code {exit_code}")

            # Read any error output
            if self.ffmpeg_process.stderr:
                try:
                    error_output = self.ffmpeg_process.stderr.read().decode('utf-8', errors='ignore')
                    if error_output:
                        logger.error(f"FFmpeg error output: {error_output}")
                except:
                    pass

            return False

        try:
            # Write WebM/Opus data to ffmpeg stdin
            # ffmpeg will convert it to linear16 PCM and output to stdout
            # The converter thread will read from stdout and send to Deepgram
            logger.debug(f"📥 Received {len(audio_data)} bytes from client, writing to ffmpeg")
            self.ffmpeg_process.stdin.write(audio_data)
            self.ffmpeg_process.stdin.flush()
            logger.debug(f"✅ Wrote {len(audio_data)} bytes to ffmpeg stdin")
            return True
        except BrokenPipeError:
            logger.error(f"❌ BrokenPipeError: ffmpeg stdin pipe is broken (process may have crashed)")
            # Mark process as dead
            if self.ffmpeg_process:
                try:
                    self.ffmpeg_process.kill()
                except:
                    pass
            return False
        except Exception as e:
            logger.error(f"❌ Error sending audio to ffmpeg: {e}", exc_info=True)
            return False

    async def finish(self):
        """Signal end of audio stream."""
        # Close ffmpeg stdin to signal end of input
        if self.ffmpeg_process and self.ffmpeg_process.stdin:
            try:
                self.ffmpeg_process.stdin.close()
                logger.info("FFmpeg input stream closed")
            except Exception as e:
                logger.error(f"Error closing ffmpeg stdin: {e}", exc_info=True)

        if self.connection:
            try:
                await self.connection.close()
                logger.info("Deepgram stream finished")
            except Exception as e:
                logger.error(f"Error finishing stream: {e}", exc_info=True)

    async def disconnect(self):
        """Close WebSocket connection and cleanup ffmpeg process."""
        logger.info("🔌 Disconnecting Deepgram service...")

        # Cancel listening task
        if self.listening_task and not self.listening_task.done():
            self.listening_task.cancel()
            try:
                await self.listening_task
            except asyncio.CancelledError:
                pass
            logger.debug("Deepgram listening task cancelled")

        # Use centralized cleanup for ffmpeg
        self._cleanup_ffmpeg()

        # Close Deepgram connection
        if self.connection:
            try:
                await self.connection.close()
                self.is_connected = False
                self.connection = None
                logger.info("Deepgram WebSocket disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting: {e}", exc_info=True)


# For backward compatibility - batch transcription fallback
class DeepgramBatchService:
    def __init__(self):
        self.client = AsyncDeepgramClient(api_key=settings.DEEPGRAM_API_KEY)
        self.model = getattr(settings, 'DEEPGRAM_MODEL', 'nova-3')

    async def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        """Batch transcription (fallback, slower)."""
        if not audio_data or len(audio_data) < 1000:
            return ""

        try:
            response = await self.client.listen.v1.media.transcribe_file(
                request=audio_data,
                model=self.model,
                language=language,
                smart_format=True,
                punctuate=True,
            )

            if response and response.results and response.results.channels:
                return response.results.channels[0].alternatives[0].transcript.strip()
            return ""
        except Exception as e:
            logger.error(f"Batch transcription error: {e}")
            return ""


# Primary service: streaming
deepgram_service = DeepgramStreamingService()

# Fallback service: batch
deepgram_batch_service = DeepgramBatchService()
