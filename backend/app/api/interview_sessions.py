"""
Interview Session API - Track interview sessions with memory and export
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from supabase import Client

from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/interview-sessions", tags=["interview-sessions"])


# Pydantic models
class SessionCreate(BaseModel):
    title: Optional[str] = "Interview Session"
    session_type: str = "practice"  # practice, mock, real


class SessionUpdate(BaseModel):
    title: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None  # active, paused, completed, abandoned


class MessageCreate(BaseModel):
    role: str  # interviewer, candidate, system
    message_type: str  # question, answer, transcription, note
    content: str
    question_type: Optional[str] = None
    source: Optional[str] = None
    matched_qa_pair_id: Optional[str] = None
    examples_used: Optional[List[str]] = []
    confidence_score: Optional[float] = None


class SessionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    session_type: str
    status: str
    started_at: str
    ended_at: Optional[str]
    duration_seconds: Optional[int]
    question_count: int
    notes: Optional[str]
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    message_type: str
    content: str
    question_type: Optional[str]
    source: Optional[str]
    matched_qa_pair_id: Optional[str]
    examples_used: Optional[List[str]]
    timestamp: str
    sequence_number: Optional[int]
    confidence_score: Optional[float]


class SessionHistoryResponse(BaseModel):
    session: SessionResponse
    messages: List[MessageResponse]
    examples_used: List[str]  # All unique examples used in this session


@router.post("/{user_id}/start", response_model=SessionResponse)
async def start_session(
    user_id: str,
    session: SessionCreate,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Start a new interview session.
    Returns session_id to track all Q&A during the interview.
    """
    try:
        data = {
            "user_id": user_id,
            "title": session.title,
            "session_type": session.session_type,
            "status": "active",
            "started_at": datetime.utcnow().isoformat()
        }

        result = supabase.table("interview_sessions").insert(data).execute()

        if not result.data:
            raise HTTPException(status_code=400, detail="Failed to create session")

        logger.info(f"Started interview session {result.data[0]['id']} for user {user_id}")
        return result.data[0]

    except Exception as e:
        logger.error(f"Error starting session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/end", response_model=SessionResponse)
async def end_session(
    session_id: str,
    supabase: Client = Depends(get_supabase_client)
):
    """
    End an interview session.
    Updates status to 'completed', sets ended_at, and calculates statistics.
    """
    try:
        # Use the database function to end session and update stats
        result = supabase.rpc("end_interview_session", {
            "session_id_param": session_id
        }).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Session not found")

        logger.info(f"Ended interview session {session_id}")
        return result.data

    except Exception as e:
        logger.error(f"Error ending session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    updates: SessionUpdate,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Update session metadata (title, notes, status).
    """
    try:
        data = {k: v for k, v in updates.dict().items() if v is not None}
        data["updated_at"] = datetime.utcnow().isoformat()

        if not data:
            raise HTTPException(status_code=400, detail="No update fields provided")

        result = supabase.table("interview_sessions").update(data).eq(
            "id", session_id
        ).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Session not found")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/messages", response_model=MessageResponse)
async def add_message(
    session_id: str,
    message: MessageCreate,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Add a message (question or answer) to the session.
    Tracks examples used to avoid repetition.
    """
    try:
        # Get current message count for sequence number
        count_result = supabase.table("session_messages").select(
            "sequence_number", count="exact"
        ).eq("session_id", session_id).execute()

        sequence_number = (count_result.count or 0) + 1

        data = {
            "session_id": session_id,
            "role": message.role,
            "message_type": message.message_type,
            "content": message.content,
            "question_type": message.question_type,
            "source": message.source,
            "matched_qa_pair_id": message.matched_qa_pair_id,
            "examples_used": message.examples_used or [],
            "sequence_number": sequence_number,
            "confidence_score": message.confidence_score,
            "timestamp": datetime.utcnow().isoformat()
        }

        result = supabase.table("session_messages").insert(data).execute()

        if not result.data:
            raise HTTPException(status_code=400, detail="Failed to add message")

        return result.data[0]

    except Exception as e:
        logger.error(f"Error adding message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(
    session_id: str,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get full session history including all messages and examples used.
    Used for:
    - Passing to Claude for context
    - Displaying session replay
    - Export preparation
    """
    try:
        # Get session details
        session_result = supabase.table("interview_sessions").select("*").eq(
            "id", session_id
        ).execute()

        if not session_result.data:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get all messages
        messages_result = supabase.rpc("get_session_history", {
            "session_id_param": session_id
        }).execute()

        # Get all examples used (to avoid repetition)
        examples_result = supabase.rpc("get_session_examples", {
            "session_id_param": session_id
        }).execute()

        examples_used = [row["example"] for row in (examples_result.data or [])]

        return {
            "session": session_result.data[0],
            "messages": messages_result.data or [],
            "examples_used": examples_used
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/sessions", response_model=List[SessionResponse])
async def list_user_sessions(
    user_id: str,
    status: Optional[str] = None,
    limit: int = 20,
    supabase: Client = Depends(get_supabase_client)
):
    """
    List all interview sessions for a user.
    Optionally filter by status.
    """
    try:
        query = supabase.table("interview_sessions").select("*").eq("user_id", user_id)

        if status:
            query = query.eq("status", status)

        result = query.order("started_at", desc=True).limit(limit).execute()

        return result.data or []

    except Exception as e:
        logger.error(f"Error listing sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Delete an interview session and all its messages.
    (Cascade delete via foreign key)
    """
    try:
        result = supabase.table("interview_sessions").delete().eq(
            "id", session_id
        ).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Session not found")

        logger.info(f"Deleted interview session {session_id}")
        return {"message": "Session deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/export")
async def export_session(
    session_id: str,
    format: str = "json",  # json, markdown, text
    supabase: Client = Depends(get_supabase_client)
):
    """
    Export session for review/sharing.
    Formats: json, markdown, text
    """
    try:
        # Get full session history
        history = await get_session_history(session_id, supabase)

        if format == "json":
            return history

        elif format == "markdown":
            # Format as markdown
            md = f"# {history['session']['title']}\n\n"
            md += f"**Date**: {history['session']['started_at']}\n"
            md += f"**Duration**: {history['session'].get('duration_seconds', 0) // 60} minutes\n"
            md += f"**Questions**: {history['session']['question_count']}\n\n"
            md += "---\n\n"

            for msg in history['messages']:
                if msg['message_type'] == 'question':
                    md += f"## Q: {msg['content']}\n\n"
                elif msg['message_type'] == 'answer':
                    md += f"**A**: {msg['content']}\n\n"
                    if msg.get('examples_used'):
                        md += f"*Examples used: {', '.join(msg['examples_used'])}*\n\n"

            return {"content": md, "filename": f"interview_session_{session_id}.md"}

        elif format == "text":
            # Plain text format
            text = f"{history['session']['title']}\n"
            text += f"{'='*50}\n\n"

            for msg in history['messages']:
                if msg['message_type'] == 'question':
                    text += f"Q: {msg['content']}\n\n"
                elif msg['message_type'] == 'answer':
                    text += f"A: {msg['content']}\n\n"

            return {"content": text, "filename": f"interview_session_{session_id}.txt"}

        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use: json, markdown, or text")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
