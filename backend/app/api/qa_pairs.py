"""
Q&A Pairs API endpoints
Manage user-uploaded expected interview questions and answers
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from supabase import Client

from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/qa-pairs", tags=["qa-pairs"])


# Pydantic models
class QAPairCreate(BaseModel):
    question: str
    answer: str
    question_type: str  # behavioral, technical, situational, general
    source: str = "manual"


class QAPairUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    question_type: Optional[str] = None


class QAPairResponse(BaseModel):
    id: str
    user_id: str
    question: str
    answer: str
    question_type: str
    source: str
    usage_count: int
    last_used_at: Optional[str]
    created_at: str
    updated_at: str


class BulkParseRequest(BaseModel):
    text: str  # Free-form text containing Q&A pairs


class BulkParseResponse(BaseModel):
    parsed_pairs: List[QAPairCreate]
    count: int


@router.get("/{user_id}", response_model=List[QAPairResponse])
async def list_qa_pairs(
    user_id: str,
    question_type: Optional[str] = None,
    supabase: Client = Depends(get_supabase_client)
):
    """
    List all Q&A pairs for a user, optionally filtered by question type.
    """
    try:
        query = supabase.table("qa_pairs").select("*").eq("user_id", user_id)

        if question_type:
            query = query.eq("question_type", question_type)

        result = query.order("created_at", desc=True).execute()

        return result.data
    except Exception as e:
        logger.error(f"Error fetching Q&A pairs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}", response_model=QAPairResponse)
async def create_qa_pair(
    user_id: str,
    qa_pair: QAPairCreate,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Create a single Q&A pair.
    """
    try:
        data = {
            "user_id": user_id,
            "question": qa_pair.question,
            "answer": qa_pair.answer,
            "question_type": qa_pair.question_type,
            "source": qa_pair.source,
        }

        result = supabase.table("qa_pairs").insert(data).execute()

        if not result.data:
            raise HTTPException(status_code=400, detail="Failed to create Q&A pair")

        return result.data[0]
    except Exception as e:
        logger.error(f"Error creating Q&A pair: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/bulk-parse", response_model=BulkParseResponse)
async def bulk_parse_qa_pairs(
    user_id: str,
    request: BulkParseRequest,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Parse free-form text containing Q&A pairs using Claude AI.
    Returns parsed pairs without saving them (user can review and confirm).
    """
    try:
        # Import here to avoid circular dependency
        from app.services.claude import claude_service

        # Use Claude to extract Q&A pairs from free-form text
        parsed_pairs = await claude_service.extract_qa_pairs(request.text)

        return {
            "parsed_pairs": parsed_pairs,
            "count": len(parsed_pairs)
        }
    except Exception as e:
        logger.error(f"Error parsing Q&A pairs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/bulk-upload", response_model=List[QAPairResponse])
async def bulk_upload_qa_pairs(
    user_id: str,
    qa_pairs: List[QAPairCreate],
    supabase: Client = Depends(get_supabase_client)
):
    """
    Bulk upload multiple Q&A pairs (after user confirms parsed results).
    """
    try:
        data = [
            {
                "user_id": user_id,
                "question": pair.question,
                "answer": pair.answer,
                "question_type": pair.question_type,
                "source": pair.source,
            }
            for pair in qa_pairs
        ]

        result = supabase.table("qa_pairs").insert(data).execute()

        if not result.data:
            raise HTTPException(status_code=400, detail="Failed to upload Q&A pairs")

        logger.info(f"Bulk uploaded {len(result.data)} Q&A pairs for user {user_id}")
        return result.data
    except Exception as e:
        logger.error(f"Error bulk uploading Q&A pairs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{qa_pair_id}", response_model=QAPairResponse)
async def update_qa_pair(
    qa_pair_id: str,
    updates: QAPairUpdate,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Update a Q&A pair.
    """
    try:
        # Build update dict with only provided fields
        data = {k: v for k, v in updates.dict().items() if v is not None}

        if not data:
            raise HTTPException(status_code=400, detail="No update fields provided")

        result = supabase.table("qa_pairs").update(data).eq("id", qa_pair_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Q&A pair not found")

        return result.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Q&A pair: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{qa_pair_id}")
async def delete_qa_pair(
    qa_pair_id: str,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Delete a Q&A pair.
    """
    try:
        result = supabase.table("qa_pairs").delete().eq("id", qa_pair_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Q&A pair not found")

        return {"message": "Q&A pair deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting Q&A pair: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{qa_pair_id}/increment-usage")
async def increment_usage(
    qa_pair_id: str,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Increment usage count and update last_used_at when a Q&A pair is used.
    """
    try:
        # Fetch current usage count
        current = supabase.table("qa_pairs").select("usage_count").eq("id", qa_pair_id).execute()

        if not current.data:
            raise HTTPException(status_code=404, detail="Q&A pair not found")

        new_count = current.data[0]["usage_count"] + 1

        # Update usage count and last_used_at
        result = supabase.table("qa_pairs").update({
            "usage_count": new_count,
            "last_used_at": "now()"
        }).eq("id", qa_pair_id).execute()

        return {"usage_count": new_count}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error incrementing usage: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
