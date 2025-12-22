"""
WebSocket endpoint for real-time audio transcription with session memory
"""

import json
import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.deepgram_service import deepgram_service
from app.services.claude import claude_service, detect_question_fast
from app.services.llm_service import llm_service
from app.core.supabase import get_supabase_client

# 로거 설정
logger = logging.getLogger(__name__)

router = APIRouter()


# Helper functions for session management
async def create_interview_session(user_id: str, title: str = "Interview Practice") -> str:
    """Create a new interview session and return session_id"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("interview_sessions").insert({
            "user_id": user_id,
            "title": title,
            "status": "active",
            "started_at": datetime.utcnow().isoformat()
        }).execute()

        if result.data:
            session_id = result.data[0]["id"]
            logger.info(f"Created interview session: {session_id}")
            return session_id
        return None
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        return None


async def save_session_message(
    session_id: str,
    role: str,
    message_type: str,
    content: str,
    question_type: str = None,
    source: str = None,
    examples_used: list = None
):
    """Save a message to the interview session"""
    try:
        supabase = get_supabase_client()

        # Get sequence number
        count_result = supabase.table("session_messages").select(
            "sequence_number", count="exact"
        ).eq("session_id", session_id).execute()

        sequence_number = (count_result.count or 0) + 1

        data = {
            "session_id": session_id,
            "role": role,
            "message_type": message_type,
            "content": content,
            "question_type": question_type,
            "source": source,
            "examples_used": examples_used or [],
            "sequence_number": sequence_number,
            "message_timestamp": datetime.utcnow().isoformat()
        }

        supabase.table("session_messages").insert(data).execute()
        logger.debug(f"Saved session message ({role}/{message_type})")

    except Exception as e:
        logger.error(f"Failed to save session message: {e}")


async def get_session_history(session_id: str) -> list:
    """Get session history for context"""
    try:
        supabase = get_supabase_client()
        result = supabase.rpc("get_session_history", {
            "session_id_param": session_id
        }).execute()

        return result.data or []
    except Exception as e:
        logger.error(f"Failed to get session history: {e}")
        return []


async def get_session_examples(session_id: str) -> list:
    """Get all examples used in session"""
    try:
        supabase = get_supabase_client()
        result = supabase.rpc("get_session_examples", {
            "session_id_param": session_id
        }).execute()

        return [row["example"] for row in (result.data or [])]
    except Exception as e:
        logger.error(f"Failed to get session examples: {e}")
        return []


async def end_interview_session(session_id: str):
    """End interview session"""
    try:
        supabase = get_supabase_client()
        supabase.rpc("end_interview_session", {
            "session_id_param": session_id
        }).execute()

        logger.info(f"Ended interview session: {session_id}")
    except Exception as e:
        logger.error(f"Failed to end session: {e}")


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

    # Session memory (NEW: track session for memory and export)
    session_id = None
    session_examples_used = []  # Track examples used to avoid repetition

    logger.info("WebSocket transcription session started")

    # Send immediate acknowledgment
    try:
        await manager.send_json(websocket, {
            "type": "connected",
            "message": "WebSocket connected successfully"
        })
        logger.info("Sent connection acknowledgment to client")
    except Exception as e:
        logger.error(f"Failed to send connection ack: {e}")

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

                        # NEW: Save question to session
                        if session_id:
                            await save_session_message(
                                session_id=session_id,
                                role="interviewer",
                                message_type="question",
                                content=question,
                                question_type=question_type,
                                source="detected"
                            )

                        await manager.send_json(websocket, {
                            "type": "question_detected",
                            "question": question,
                            "question_type": question_type
                        })

                        # Auto-generate answer with RAG approach
                        # 1. Send temporary answer immediately
                        temp_answer = claude_service.get_temporary_answer(question_type)
                        await manager.send_json(websocket, {
                            "type": "answer_temporary",
                            "question": question,
                            "answer": temp_answer
                        })

                        # 2. Generate answer using RAG (handles both simple and complex questions)
                        # RAG will automatically:
                        # - Find single exact match for simple questions (return directly)
                        # - Find multiple relevant Q&A pairs for complex questions (synthesize)
                        logger.info("Generating answer with RAG approach")

                        # NEW: Get session history and examples for context
                        session_history = await get_session_history(session_id) if session_id else []
                        session_examples = await get_session_examples(session_id) if session_id else []
                        logger.info(f"Using session context: {len(session_history)} messages, {len(session_examples)} examples used")

                        # Signal streaming start
                        await manager.send_json(websocket, {
                            "type": "answer_stream_start",
                            "question": question,
                            "source": "generated"
                        })

                        # Debug logging
                        logger.warning("=" * 80)
                        logger.warning(f"RAG_DEBUG: Starting answer generation for question: {question}")
                        logger.warning(f"RAG_DEBUG: Context has {len(user_context.get('qa_pairs', []))} Q&A pairs")
                        logger.warning(f"RAG_DEBUG: user_id={user_profile.get('user_id') if user_profile else 'None'}")
                        logger.warning("=" * 80)

                        # Stream answer chunks in real-time with RAG
                        generated_answer = ""
                        async for chunk in llm_service.generate_answer_stream(
                            question=question,
                            resume_text=user_context["resume_text"],
                            star_stories=user_context["star_stories"],
                            talking_points=user_context["talking_points"],
                            qa_pairs=user_context["qa_pairs"],  # Pass Q&A pairs for RAG
                            format="bullet",  # Bullet point format for real-time interview
                            user_profile=user_profile,
                            session_history=session_history,
                            examples_used=session_examples
                        ):
                            generated_answer += chunk
                            await manager.send_json(websocket, {
                                "type": "answer_stream_chunk",
                                "question": question,
                                "chunk": chunk,
                                "source": "generated"
                            })

                        # NEW: Extract examples and save generated answer to session
                        if session_id and generated_answer:
                            # Extract examples from answer
                            import re
                            new_examples = []
                            example_patterns = re.findall(
                                r'(?:Project|at|working on|led|built)\s+([A-Z][A-Za-z0-9\s]{2,30})',
                                generated_answer
                            )
                            for match in example_patterns:
                                cleaned = match.strip()
                                if len(cleaned) > 3 and cleaned not in session_examples:
                                    new_examples.append(cleaned)

                            logger.info(f"Extracted {len(new_examples)} new examples: {new_examples}")

                            await save_session_message(
                                session_id=session_id,
                                role="candidate",
                                message_type="answer",
                                content=generated_answer,
                                question_type=question_type,
                                source="ai_generated",
                                examples_used=new_examples
                            )

                            # Update local tracking
                            session_examples_used.extend(new_examples)

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
        logger.info("Attempting to create Deepgram connection...")
        async with deepgram_service.create_connection(
            on_transcript=on_transcript,
            on_error=on_error
        ) as dg_connection:
            logger.info("Deepgram connection created, setting up handlers...")
            # Set up event handlers and start listening
            await deepgram_service.setup_connection(dg_connection)
            deepgram_connected = True
            logger.info("✓ Deepgram connected and ready")

            # Notify client that transcription is ready
            await manager.send_json(websocket, {
                "type": "transcription_ready",
                "message": "Speech recognition ready"
            })

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
                            # Update user context
                            user_context["resume_text"] = data.get("resume_text", "")
                            user_context["star_stories"] = data.get("star_stories", [])
                            user_context["talking_points"] = data.get("talking_points", [])
                            user_context["qa_pairs"] = data.get("qa_pairs", [])

                            # Extract user_id if provided
                            received_user_id = data.get("user_id")
                            logger.warning(f"CONTEXT_DEBUG: Received user_id from frontend: {received_user_id}")
                            logger.warning(f"CONTEXT_DEBUG: Current user_id in WebSocket: {user_id}")
                            logger.warning(f"CONTEXT_DEBUG: Full context message keys: {list(data.keys())}")

                            if received_user_id and received_user_id != user_id:
                                logger.warning(f"CONTEXT_DEBUG: Switching user_id from {user_id} to {received_user_id}")
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

                                # NEW: Create interview session for memory tracking
                                if not session_id:
                                    session_id = await create_interview_session(user_id, "Interview Practice")
                                    if session_id:
                                        logger.info(f"Created session {session_id} for user {user_id}")

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
                            # NEW: End current session before clearing
                            if session_id:
                                await end_interview_session(session_id)
                                session_id = None
                                session_examples_used = []

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

                                    # NEW: Get session history and examples
                                    session_history = await get_session_history(session_id) if session_id else []
                                    session_examples = await get_session_examples(session_id) if session_id else []

                                    # Signal streaming start
                                    await manager.send_json(websocket, {
                                        "type": "answer_stream_start",
                                        "question": question,
                                        "source": "generated"
                                    })

                                    # Stream answer chunks in real-time
                                    generated_answer = ""
                                    async for chunk in llm_service.generate_answer_stream(
                                        question=question,
                                        resume_text=user_context["resume_text"],
                                        star_stories=user_context["star_stories"],
                                        talking_points=user_context["talking_points"],
                                        qa_pairs=user_context["qa_pairs"],  # Pass Q&A pairs for reference
                                        format="bullet",  # Bullet point format for real-time interview
                                        user_profile=user_profile,
                                        session_history=session_history,
                                        examples_used=session_examples
                                    ):
                                        generated_answer += chunk
                                        await manager.send_json(websocket, {
                                            "type": "answer_stream_chunk",
                                            "question": question,
                                            "chunk": chunk,
                                            "source": "generated"
                                        })

                                    # NEW: Save answer with extracted examples
                                    if session_id and generated_answer:
                                        import re
                                        new_examples = []
                                        example_patterns = re.findall(
                                            r'(?:Project|at|working on|led|built)\s+([A-Z][A-Za-z0-9\s]{2,30})',
                                            generated_answer
                                        )
                                        for match in example_patterns:
                                            cleaned = match.strip()
                                            if len(cleaned) > 3 and cleaned not in session_examples:
                                                new_examples.append(cleaned)

                                        await save_session_message(
                                            session_id=session_id,
                                            role="candidate",
                                            message_type="answer",
                                            content=generated_answer,
                                            question_type=question_type,
                                            source="ai_generated",
                                            examples_used=new_examples
                                        )
                                        session_examples_used.extend(new_examples)

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
    except asyncio.TimeoutError:
        logger.error("TIMEOUT: Deepgram connection timed out", exc_info=True)
        try:
            await manager.send_json(websocket, {
                "type": "error",
                "message": "Connection timeout - please refresh and try again"
            })
        except:
            pass
    except Exception as e:
        logger.error(f"WebSocket error: {type(e).__name__}: {str(e)}", exc_info=True)
        try:
            await manager.send_json(websocket, {
                "type": "error",
                "message": f"Connection error: {str(e)}"
            })
        except:
            pass
    finally:
        # NEW: End session on disconnect
        if session_id:
            await end_interview_session(session_id)
            logger.info(f"Ended session {session_id} on disconnect")

        # Deepgram connection is automatically closed by context manager
        manager.disconnect(websocket)
        logger.info("WebSocket session ended")