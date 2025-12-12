"""
WebSocket endpoint for real-time audio transcription
"""

import json
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.whisper import whisper_service
from app.services.claude import claude_service

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_json(self, websocket: WebSocket, data: dict) -> bool:
        try:
            await websocket.send_json(data)
            logger.debug(f"Sent message: {data.get('type', 'unknown')}")
            return True
        except RuntimeError as e:
            if "close message" in str(e) or "disconnect" in str(e).lower():
                logger.info(f"Client disconnected while sending message: {data.get('type')}")
                return False
            logger.error(f"Error sending message: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False


manager = ConnectionManager()


def is_likely_question(text: str) -> bool:
    """
    Quick pre-filter to check if text might be a question.
    This is a fast keyword-based check to avoid unnecessary Claude API calls.

    Args:
        text: The transcribed text

    Returns:
        True if text might be a question, False if definitely not
    """
    if not text or len(text) < 5:
        return False

    text_lower = text.lower().strip()

    # Question indicators
    question_words = [
        'what', 'how', 'why', 'when', 'where', 'who', 'which', 'whose',
        'can you', 'could you', 'would you', 'will you', 'should you',
        'do you', 'did you', 'does', 'have you', 'has',
        'describe', 'tell me', 'explain', 'share', 'talk about',
        'give me', 'walk me through', 'think of'
    ]

    # Check for question mark
    if '?' in text:
        return True

    # Check if starts with question word
    if any(text_lower.startswith(q) for q in question_words):
        return True

    # Check if contains question word
    if any(f" {q} " in f" {text_lower} " for q in question_words):
        return True

    # If text is very short and has no question indicators, likely not a question
    if len(text.split()) < 8:
        return False

    # For longer text without clear indicators, let Claude decide
    return True


def is_question_likely_complete(text: str) -> bool:
    """
    Check if a question appears to be complete.

    Args:
        text: The transcribed text

    Returns:
        True if the question appears complete, False otherwise
    """
    if not text:
        return False

    text = text.strip()

    # Check minimum word count (at least 5 words)
    word_count = len(text.split())
    if word_count < 5:
        return False

    # Check if it ends with question mark or other terminal punctuation
    # Some questions may not have ?, so we're lenient here
    has_terminal_punctuation = text.endswith('?') or text.endswith('.') or text.endswith('!')

    # If it has a question mark, it's likely complete
    if text.endswith('?'):
        return True

    # If it has reasonable length and some punctuation or is long enough
    if word_count >= 8:
        return True

    return has_terminal_punctuation


@router.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio transcription.

    Client sends:
        - Binary audio data (WAV format chunks)
        - JSON messages: {"type": "config", "language": "en"}

    Server sends:
        - {"type": "transcription", "text": "...", "is_final": bool}
        - {"type": "question_detected", "question": "...", "question_type": "..."}
        - {"type": "answer", "answer": "..."}
        - {"type": "error", "message": "..."}
    """
    await manager.connect(websocket)

    # Session state
    audio_buffer = bytearray()
    language = "en"
    user_context = {
        "resume_text": "",
        "star_stories": [],
        "talking_points": []
    }
    accumulated_text = ""
    last_process_time = asyncio.get_event_loop().time()
    is_processing = False
    audio_chunk_count = 0
    total_audio_bytes = 0
    last_processed_question = ""
    last_transcribed_text = ""  # Track what we already transcribed

    logger.info("WebSocket transcription session started")

    try:
        while True:
            message = await websocket.receive()

            if "bytes" in message:
                # Audio data received
                audio_chunk_count += 1
                chunk_size = len(message["bytes"])
                total_audio_bytes += chunk_size
                audio_buffer.extend(message["bytes"])
                
                current_time = asyncio.get_event_loop().time()
                
                logger.debug(f"Audio chunk #{audio_chunk_count}: {chunk_size} bytes, buffer: {len(audio_buffer)} bytes")

                # Limit buffer size to prevent memory issues and slow processing
                # Keep only last 30 seconds of audio (30 * 16000 * 2 = 960000 bytes)
                MAX_BUFFER_SIZE = 960000
                if len(audio_buffer) > MAX_BUFFER_SIZE:
                    # Remove oldest audio (keep last 30 seconds)
                    bytes_to_remove = len(audio_buffer) - MAX_BUFFER_SIZE
                    audio_buffer = audio_buffer[bytes_to_remove:]
                    logger.info(f"Buffer trimmed to {len(audio_buffer)} bytes")

                # Process when we have enough audio (about 2 seconds worth at 16kHz)
                # 16000 samples/sec * 2 bytes * 2 sec = 64000 bytes
                # 또는 마지막 처리 후 2.0초가 지났을 때도 처리 (타임아웃 메커니즘)
                buffer_threshold_reached = len(audio_buffer) >= 64000
                timeout_reached = (current_time - last_process_time >= 2.0 and len(audio_buffer) > 32000)
                
                if (buffer_threshold_reached or timeout_reached) and not is_processing:
                    is_processing = True
                    # Send entire accumulated buffer (not clearing it)
                    # This creates a valid WebM file from accumulated chunks
                    audio_data = bytes(audio_buffer)
                    last_process_time = current_time
                    
                    logger.info(f"Processing audio: {len(audio_data)} bytes (chunk #{audio_chunk_count})")

                    try:
                        # Transcribe audio
                        transcription = await whisper_service.transcribe(
                            audio_data,
                            language=language
                        )

                        if transcription:
                            # Use the transcription as-is (Whisper already handles the full buffer)
                            accumulated_text = transcription.strip()

                            logger.info(f"Transcription: '{accumulated_text}'")

                            # Send transcription to client
                            sent = await manager.send_json(websocket, {
                                "type": "transcription",
                                "text": "", # accumulated_text contains everything
                                "accumulated_text": accumulated_text,
                                "is_final": False,
                                "chunk_count": audio_chunk_count
                            })
                            if not sent:
                                break

                            # Pre-filter: Quick check if this looks like a question
                            if not is_likely_question(accumulated_text):
                                logger.debug(f"Text does not appear to be a question, skipping Claude detection: '{accumulated_text[:50]}...'")
                                continue

                            # Check if it's a question using Claude
                            detection = await claude_service.detect_question(accumulated_text)

                            if detection["is_question"] and detection["question"]:
                                # Validate question completeness
                                if not is_question_likely_complete(detection["question"]):
                                    logger.info(f"Question detected but appears incomplete: '{detection['question']}' - waiting for more input")
                                    continue

                                logger.info(f"Complete question detected: '{detection['question']}' ({detection['question_type']})")

                                sent = await manager.send_json(websocket, {
                                    "type": "question_detected",
                                    "question": detection["question"],
                                    "question_type": detection["question_type"]
                                })
                                if not sent:
                                    break

                                # Check if we already answered this question (fuzzy match)
                                question_normalized = detection["question"].strip().lower()
                                last_normalized = last_processed_question.lower()

                                # If questions are very similar (same start or 80% overlap), skip
                                if last_normalized and (
                                    question_normalized.startswith(last_normalized[:20]) or
                                    last_normalized.startswith(question_normalized[:20])
                                ):
                                    logger.info(f"Skipping answer generation for similar question: '{detection['question']}'")
                                    continue

                                last_processed_question = detection["question"].strip()

                                # Generate answer
                                answer = await claude_service.generate_answer(
                                    question=detection["question"],
                                    resume_text=user_context["resume_text"],
                                    star_stories=user_context["star_stories"],
                                    talking_points=user_context["talking_points"]
                                )

                                sent = await manager.send_json(websocket, {
                                    "type": "answer",
                                    "question": detection["question"],
                                    "answer": answer
                                })
                                if not sent:
                                    break

                                # Reset accumulated text after generating answer
                                accumulated_text = ""
                                logger.info("Reset accumulated text after answer generation")
                        else:
                            logger.warning("Empty transcription result")
                    
                    except Exception as e:
                        logger.error(f"Error processing audio chunk #{audio_chunk_count}: {str(e)}", exc_info=True)
                        await manager.send_json(websocket, {
                            "type": "error",
                            "message": f"Error processing audio: {str(e)}"
                        })
                    finally:
                        is_processing = False

            elif "text" in message:
                # JSON message received
                try:
                    data = json.loads(message["text"])
                    msg_type = data.get("type", "")
                    logger.info(f"Received JSON message: {msg_type}")

                    if msg_type == "config":
                        language = data.get("language", "en")
                        logger.info(f"Language configured to: {language}")
                        await manager.send_json(websocket, {
                            "type": "config_ack",
                            "language": language
                        })

                    elif msg_type == "context":
                        # Update user context
                        user_context["resume_text"] = data.get("resume_text", "")
                        user_context["star_stories"] = data.get("star_stories", [])
                        user_context["talking_points"] = data.get("talking_points", [])
                        logger.info(f"Context updated: {len(user_context['star_stories'])} stories, {len(user_context['talking_points'])} points")
                        await manager.send_json(websocket, {
                            "type": "context_ack",
                            "message": "Context updated"
                        })

                    elif msg_type == "clear":
                        # Clear accumulated text and answer cache
                        accumulated_text = ""
                        audio_buffer.clear()
                        audio_chunk_count = 0
                        total_audio_bytes = 0
                        last_processed_question = ""
                        last_transcribed_text = ""
                        claude_service.clear_cache()
                        logger.info("Session cleared, including answer cache")
                        await manager.send_json(websocket, {
                            "type": "cleared",
                            "message": "Session cleared"
                        })

                    elif msg_type == "generate_answer":
                        # Manual answer generation request
                        question = data.get("question", "")
                        if question:
                            logger.info(f"Manual answer generation for: '{question}'")
                            answer = await claude_service.generate_answer(
                                question=question,
                                resume_text=user_context["resume_text"],
                                star_stories=user_context["star_stories"],
                                talking_points=user_context["talking_points"]
                            )
                            await manager.send_json(websocket, {
                                "type": "answer",
                                "question": question,
                                "answer": answer
                            })

                    elif msg_type == "finalize":
                        # Process any remaining audio
                        if len(audio_buffer) > 0:
                            logger.info(f"Finalizing: processing remaining {len(audio_buffer)} bytes")
                            audio_data = bytes(audio_buffer)
                            # Keep buffer for context, will be cleared on next "clear" message

                            transcription = await whisper_service.transcribe(
                                audio_data,
                                language=language
                            )

                            if transcription:
                                accumulated_text = transcription
                                accumulated_text = accumulated_text.strip()

                                await manager.send_json(websocket, {
                                    "type": "transcription",
                                    "text": transcription,
                                    "accumulated_text": accumulated_text,
                                    "is_final": True
                                })

                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {str(e)}")
                    await manager.send_json(websocket, {
                        "type": "error",
                        "message": "Invalid JSON message"
                    })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected after {audio_chunk_count} chunks, {total_audio_bytes} total bytes")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        manager.disconnect(websocket)