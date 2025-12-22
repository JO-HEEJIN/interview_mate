"""
Q&A Pairs API endpoints
Manage user-uploaded expected interview questions and answers
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from supabase import Client

from app.core.supabase import get_supabase_client
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/qa-pairs", tags=["qa-pairs"])


# Qdrant service instance (lazy initialization)
_qdrant_service = None


def get_qdrant_service():
    """Get or create Qdrant service instance"""
    global _qdrant_service
    if _qdrant_service is None and settings.QDRANT_URL:
        from app.services.qdrant_service import QdrantService
        _qdrant_service = QdrantService(
            qdrant_url=settings.QDRANT_URL,
            openai_api_key=settings.OPENAI_API_KEY
        )
    return _qdrant_service


async def sync_qa_pair_to_qdrant(qa_pair: dict):
    """
    Background task to sync Q&A pair to Qdrant

    Args:
        qa_pair: Q&A pair data from Supabase
    """
    try:
        qdrant = get_qdrant_service()
        if not qdrant:
            logger.warning("Qdrant not configured, skipping sync")
            return

        # Only sync if embedding exists
        if not qa_pair.get('question_embedding'):
            logger.debug(f"Q&A {qa_pair['id']} has no embedding, skipping Qdrant sync")
            return

        await qdrant.upsert_qa_pair(
            qa_id=qa_pair['id'],
            question=qa_pair['question'],
            answer=qa_pair['answer'],
            user_id=qa_pair['user_id'],
            question_type=qa_pair.get('question_type'),
            embedding=qa_pair.get('question_embedding')
        )
        logger.info(f"Synced Q&A {qa_pair['id']} to Qdrant")

    except Exception as e:
        logger.error(f"Error syncing Q&A to Qdrant: {e}", exc_info=True)


async def delete_qa_pair_from_qdrant(qa_id: str):
    """
    Background task to delete Q&A pair from Qdrant

    Args:
        qa_id: Q&A pair ID
    """
    try:
        qdrant = get_qdrant_service()
        if not qdrant:
            return

        await qdrant.delete_qa_pair(qa_id)
        logger.info(f"Deleted Q&A {qa_id} from Qdrant")

    except Exception as e:
        logger.error(f"Error deleting Q&A from Qdrant: {e}", exc_info=True)


# Pydantic models
class QAPairCreate(BaseModel):
    question: str
    answer: str
    question_type: str  # behavioral, technical, situational, general
    source: str = "manual"
    question_variations: Optional[List[str]] = []  # Alternative question phrasings


class QAPairUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    question_type: Optional[str] = None
    question_variations: Optional[List[str]] = None  # Update variations


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
    question_variations: Optional[List[str]] = []  # Alternative question phrasings


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
    background_tasks: BackgroundTasks,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Create a single Q&A pair.
    Automatically syncs to Qdrant if embeddings are generated.
    """
    try:
        data = {
            "user_id": user_id,
            "question": qa_pair.question,
            "answer": qa_pair.answer,
            "question_type": qa_pair.question_type,
            "source": qa_pair.source,
            "question_variations": qa_pair.question_variations or [],
        }

        result = supabase.table("qa_pairs").insert(data).execute()

        if not result.data:
            raise HTTPException(status_code=400, detail="Failed to create Q&A pair")

        created_qa = result.data[0]

        # Sync to Qdrant in background (after embedding is generated)
        # Note: Embedding will be generated by a separate process/trigger
        # This sync will happen when the embedding exists
        background_tasks.add_task(sync_qa_pair_to_qdrant, created_qa)

        return created_qa
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
        from app.services.claude import get_claude_service

        # Use OpenAI Structured Outputs to extract Q&A pairs from free-form text
        # Falls back to Claude Tool Use if OpenAI fails
        claude_service = get_claude_service()
        parsed_pairs = await claude_service.extract_qa_pairs_openai(request.text)

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
                "question_variations": pair.question_variations or [],
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
    background_tasks: BackgroundTasks,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Update a Q&A pair.
    Automatically syncs to Qdrant.
    """
    try:
        # Build update dict with only provided fields
        data = {k: v for k, v in updates.dict().items() if v is not None}

        if not data:
            raise HTTPException(status_code=400, detail="No update fields provided")

        result = supabase.table("qa_pairs").update(data).eq("id", qa_pair_id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Q&A pair not found")

        updated_qa = result.data[0]

        # Sync to Qdrant in background
        background_tasks.add_task(sync_qa_pair_to_qdrant, updated_qa)

        return updated_qa
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating Q&A pair: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{qa_pair_id}")
async def delete_qa_pair(
    qa_pair_id: str,
    background_tasks: BackgroundTasks,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Delete a Q&A pair.
    Automatically removes from Qdrant.
    """
    try:
        result = supabase.table("qa_pairs").delete().eq("id", qa_pair_id).execute()

        # Delete from Qdrant in background
        background_tasks.add_task(delete_qa_pair_from_qdrant, qa_pair_id)

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


@router.post("/{user_id}/generate-embeddings")
async def generate_embeddings_for_user(
    user_id: str,
    supabase: Client = Depends(get_supabase_client)
):
    """
    Generate OpenAI embeddings for all Q&A pairs that don't have embeddings yet.

    This endpoint enables semantic similarity matching for Q&A pairs.
    Call this after:
    - Bulk uploading new Q&A pairs
    - Creating/updating individual Q&A pairs
    - Migrating from old string-matching to semantic matching

    Returns:
        {
            "success_count": int,  # Number of embeddings generated
            "failed_count": int,   # Number of failures
            "total_processed": int
        }
    """
    try:
        # Import here to avoid circular dependency
        from app.services.embedding_service import get_embedding_service

        embedding_service = get_embedding_service(supabase)

        logger.info(f"Starting embedding generation for user: {user_id}")
        success_count, failed_count = await embedding_service.update_embeddings_for_user(user_id)

        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "total_processed": success_count + failed_count
        }

    except Exception as e:
        logger.error(f"Error generating embeddings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
