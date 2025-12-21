"""
WebSocket endpoint for real-time audio transcription
"""

import json
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.deepgram_service import deepgram_service
from app.services.claude import claude_service, detect_question_fast
from app.services.llm_service import llm_service
from app.core.supabase import get_supabase_client

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter()


async def increment_qa_usage(qa_pair_id: str):
    """Increment usage count for a Q&A pair when it's used in practice"""
    try:
        supabase = get_supabase_client()

        # Fetch current usage count
        result = supabase.table("qa_pairs").select("usage_count").eq("id", qa_pair_id).execute()

        if not result.data:
            logger.warning(f"Q&A pair {qa_pair_id} not found for usage increment")
            return

        current_count = result.data[0].get("usage_count", 0)
        new_count = current_count + 1

        # Update usage count and last_used_at
        supabase.table("qa_pairs").update({
            "usage_count": new_count,
            "last_used_at": "now()"
        }).eq("id", qa_pair_id).execute()

        logger.info(f"Q&A pair {qa_pair_id} usage incremented: {current_count} → {new_count}")

    except Exception as e:
        logger.error(f"Failed to increment Q&A usage: {e}", exc_info=True)


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
    WebSocket endpoint for real-time audio transcription using Deepgram streaming.

    Client sends:
        - Binary audio data (WebM/Opus format chunks)
        - JSON messages: {"type": "config", "language": "en"}

    Server sends:
        - {"type": "transcription", "text": "...", "is_final": bool}
        - {"type": "question_detected", "question": "...", "question_type": "..."}
        - {"type": "answer", "answer": "..."}
        - {"type": "error", "message": "..."}
    """
    await manager.connect(websocket)

    # Session state
    language = "en"
    user_id = None
    user_profile = None  # Interview profile for personalized prompts
    user_context = {
        "resume_text": "",
        "star_stories": [],
        "talking_points": [],
        "qa_pairs": []  # User's uploaded Q&A pairs
    }
    accumulated_text = ""
    is_processing = False
    audio_chunk_count = 0
    total_audio_bytes = 0
    last_processed_question = ""
    deepgram_connected = False

    logger.info("WebSocket transcription session started")

    # Deepgram transcript callback
    async def on_transcript(text: str, is_final: bool):
        nonlocal accumulated_text, is_processing

        try:
            if not text.strip():
                return

            logger.info(f"Deepgram transcript ({'final' if is_final else 'interim'}): '{text}'")

            # Update accumulated text
            if is_final:
                accumulated_text = text.strip()

            # Send transcription to client
            sent = await manager.send_json(websocket, {
                "type": "transcription",
                "text": text,
                "accumulated_text": accumulated_text,
                "is_final": is_final
            })
            if not sent:
                return

            # Only process questions on final transcripts
            if is_final and not is_processing:
                is_processing = True

                try:
                    # Pre-filter: Quick check if this looks like a question
                    if not is_likely_question(accumulated_text):
                        logger.debug(f"Text does not appear to be a question: '{accumulated_text[:50]}...'")
                        return

                    # OPTIMIZATION (Phase 1.2): Fast pattern-based detection first
                    # Only fall back to Claude API if confidence is low
                    detection = detect_question_fast(accumulated_text)

                    # Fallback: Use Claude API for low-confidence cases
                    if detection["confidence"] == "low" and detection["is_question"]:
                        logger.info("Low confidence pattern match, verifying with Claude API")
                        detection = await claude_service.detect_question(accumulated_text)

                    if detection["is_question"] and detection["question"]:
                        # Validate question completeness
                        if not is_question_likely_complete(detection["question"]):
                            logger.info(f"Question incomplete: '{detection['question']}' - waiting")
                            return

                        question = detection["question"]
                        question_type = detection["question_type"]

                        logger.info(f"Complete question detected: '{question}' ({question_type})")

                        await manager.send_json(websocket, {
                            "type": "question_detected",
                            "question": question,
                            "question_type": question_type
                        })

                        # Auto-generate answer with Q&A matching
                        # 1. Send temporary answer immediately
                        temp_answer = claude_service.get_temporary_answer(question_type)
                        await manager.send_json(websocket, {
                            "type": "answer_temporary",
                            "question": question,
                            "answer": temp_answer
                        })

                        # 2. Check for uploaded Q&A match (OPTIMIZED: <1ms lookup)
                        matched_qa = claude_service.find_matching_qa_pair_fast(question)

                        if matched_qa:
                            # 3a. Return uploaded answer (instant)
                            qa_pair_id = matched_qa.get("id")
                            logger.info(f"Using uploaded Q&A pair (ID: {qa_pair_id})")

                            # Increment usage count in background
                            if qa_pair_id:
                                asyncio.create_task(increment_qa_usage(qa_pair_id))

                            await manager.send_json(websocket, {
                                "type": "answer",
                                "question": question,
                                "answer": matched_qa["answer"],
                                "source": "uploaded",
                                "qa_pair_id": qa_pair_id,
                                "is_streaming": False
                            })
                        else:
                            # 3b. Generate with streaming LLM (Phase 1.3)
                            logger.info("No matching Q&A found, generating with streaming LLM")

                            # Signal streaming start
                            await manager.send_json(websocket, {
                                "type": "answer_stream_start",
                                "question": question,
                                "source": "generated"
                            })

                            # Stream answer chunks in real-time
                            async for chunk in llm_service.generate_answer_stream(
                                question=question,
                                resume_text=user_context["resume_text"],
                                star_stories=user_context["star_stories"],
                                talking_points=user_context["talking_points"],
                                format="bullet",  # Bullet point format for real-time interview
                                user_profile=user_profile
                            ):
                                await manager.send_json(websocket, {
                                    "type": "answer_stream_chunk",
                                    "question": question,
                                    "chunk": chunk,
                                    "source": "generated"
                                })

                            # Signal streaming end
                            await manager.send_json(websocket, {
                                "type": "answer_stream_end",
                                "question": question,
                                "source": "generated"
                            })
                finally:
                    is_processing = False

        except Exception as e:
            logger.error(f"Error in transcript callback: {e}", exc_info=True)

    # Deepgram error callback
    async def on_error(error: str):
        logger.error(f"Deepgram error: {error}")
        await manager.send_json(websocket, {
            "type": "error",
            "message": f"Transcription error: {error}"
        })

    # Connect to Deepgram using context manager
    try:
        async with deepgram_service.create_connection(
            on_transcript=on_transcript,
            on_error=on_error
        ) as dg_connection:
            # Set up event handlers and start listening
            await deepgram_service.setup_connection(dg_connection)
            deepgram_connected = True

            # Main message loop
            while True:
                try:
                    message = await websocket.receive()
                except RuntimeError as e:
                    err_msg = str(e).lower()
                    if "disconnect" in err_msg or "close message" in err_msg:
                        logger.info("WebSocket disconnected during receive")
                        break
                    logger.error(f"WebSocket receive error: {e}")
                    break
                except Exception as e:
                    logger.error(f"Unexpected WebSocket error: {e}")
                    break

                if "bytes" in message:
                    # Audio data received - send immediately to Deepgram
                    audio_chunk_count += 1
                    chunk_size = len(message["bytes"])
                    total_audio_bytes += chunk_size

                    logger.debug(f"Audio chunk #{audio_chunk_count}: {chunk_size} bytes (total: {total_audio_bytes} bytes)")

                    # Send audio chunk immediately to Deepgram for real-time transcription
                    if deepgram_connected:
                        success = await deepgram_service.send_audio(message["bytes"])
                        if not success:
                            logger.warning(f"Failed to send audio chunk #{audio_chunk_count} to Deepgram")
                    else:
                        logger.warning("Deepgram not connected, skipping audio chunk")

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
                            nonlocal user_id, user_profile

                            # Update user context
                            user_context["resume_text"] = data.get("resume_text", "")
                            user_context["star_stories"] = data.get("star_stories", [])
                            user_context["talking_points"] = data.get("talking_points", [])
                            user_context["qa_pairs"] = data.get("qa_pairs", [])

                            # Extract user_id if provided
                            received_user_id = data.get("user_id")
                            if received_user_id and received_user_id != user_id:
                                user_id = received_user_id

                                # Load interview profile
                                try:
                                    supabase = get_supabase_client()
                                    profile_response = supabase.table("user_interview_profiles").select("*").eq("user_id", user_id).execute()

                                    if profile_response.data and len(profile_response.data) > 0:
                                        user_profile = profile_response.data[0]
                                        logger.info(f"Loaded interview profile for user {user_id}: {user_profile.get('full_name', 'N/A')}")
                                    else:
                                        logger.info(f"No interview profile found for user {user_id}, using defaults")
                                        user_profile = None
                                except Exception as e:
                                    logger.error(f"Failed to load interview profile: {e}", exc_info=True)
                                    user_profile = None

                            # OPTIMIZATION (Phase 1.1): Build Q&A index for fast lookup
                            # This takes <1ms and enables O(1) exact matching + faster similarity search
                            if user_context["qa_pairs"]:
                                claude_service.build_qa_index(user_context["qa_pairs"])

                            logger.info(
                                f"Context updated: {len(user_context['star_stories'])} stories, "
                                f"{len(user_context['talking_points'])} points, "
                                f"{len(user_context['qa_pairs'])} Q&A pairs"
                            )
                            await manager.send_json(websocket, {
                                "type": "context_ack",
                                "message": "Context updated",
                                "has_profile": user_profile is not None
                            })

                        elif msg_type == "clear":
                            # Clear accumulated text, answer cache, and Q&A index
                            accumulated_text = ""
                            audio_chunk_count = 0
                            total_audio_bytes = 0
                            last_processed_question = ""
                            user_context["qa_pairs"] = []
                            claude_service.clear_cache()
                            claude_service.build_qa_index([])  # Clear Q&A index
                            logger.info("Session cleared, including answer cache and Q&A index")
                            await manager.send_json(websocket, {
                                "type": "cleared",
                                "message": "Session cleared"
                            })

                        elif msg_type == "generate_answer":
                            # Manual answer generation request
                            question = data.get("question", "")
                            question_type = data.get("question_type", "general")

                            if question:
                                logger.info(f"Manual answer generation for: '{question}' (type: {question_type})")

                                # 1. Send temporary answer immediately
                                temp_answer = claude_service.get_temporary_answer(question_type)
                                await manager.send_json(websocket, {
                                    "type": "answer_temporary",
                                    "question": question,
                                    "answer": temp_answer
                                })

                                # 2. Check for uploaded Q&A match (OPTIMIZED: <1ms lookup)
                                matched_qa = claude_service.find_matching_qa_pair_fast(question)

                                if matched_qa:
                                    # 3a. Return uploaded answer (instant)
                                    qa_pair_id = matched_qa.get("id")

                                    # Increment usage count in background
                                    if qa_pair_id:
                                        asyncio.create_task(increment_qa_usage(qa_pair_id))
                                    logger.info(f"Using uploaded Q&A pair (ID: {matched_qa.get('id')})")
                                    await manager.send_json(websocket, {
                                        "type": "answer",
                                        "question": question,
                                        "answer": matched_qa["answer"],
                                        "source": "uploaded",
                                        "qa_pair_id": matched_qa.get("id"),
                                        "is_streaming": False
                                    })
                                else:
                                    # 3b. Generate with streaming LLM (Phase 1.3)
                                    logger.info("No matching Q&A found, generating with streaming LLM")

                                    # Signal streaming start
                                    await manager.send_json(websocket, {
                                        "type": "answer_stream_start",
                                        "question": question,
                                        "source": "generated"
                                    })

                                    # Stream answer chunks in real-time
                                    async for chunk in llm_service.generate_answer_stream(
                                        question=question,
                                        resume_text=user_context["resume_text"],
                                        star_stories=user_context["star_stories"],
                                        talking_points=user_context["talking_points"],
                                        format="bullet",  # Bullet point format for real-time interview
                                        user_profile=user_profile
                                    ):
                                        await manager.send_json(websocket, {
                                            "type": "answer_stream_chunk",
                                            "question": question,
                                            "chunk": chunk,
                                            "source": "generated"
                                        })

                                    # Signal streaming end
                                    await manager.send_json(websocket, {
                                        "type": "answer_stream_end",
                                        "question": question,
                                        "source": "generated"
                                    })

                        elif msg_type == "finalize":
                            # Signal end of audio stream to Deepgram
                            if deepgram_connected:
                                logger.info("Finalizing Deepgram stream")
                                await deepgram_service.finish()
                                await manager.send_json(websocket, {
                                    "type": "finalized",
                                    "message": "Audio stream finalized"
                                })

                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {str(e)}")
                        await manager.send_json(websocket, {
                            "type": "error",
                            "message": "Invalid JSON message"
                        })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected after {audio_chunk_count} chunks, {total_audio_bytes} total bytes")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
    finally:
        # Deepgram connection is automatically closed by context manager
        manager.disconnect(websocket)
        logger.info("WebSocket session ended")