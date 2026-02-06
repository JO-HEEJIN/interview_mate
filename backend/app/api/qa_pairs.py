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
    profile_id: Optional[str] = None  # Required for multi-profile support


class QAPairUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    question_type: Optional[str] = None
    question_variations: Optional[List[str]] = None  # Update variations


class QAPairResponse(BaseModel):
    id: str
    user_id: str
    profile_id: Optional[str] = None
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
    profile_id: Optional[str] = None,
    supabase: Client = Depends(get_supabase_client)
):
    """
    List all Q&A pairs for a user, optionally filtered by question type and profile.
    """
    try:
        query = supabase.table("qa_pairs").select("*").eq("user_id", user_id)

        if question_type:
            query = query.eq("question_type", question_type)

        if profile_id:
            query = query.eq("profile_id", profile_id)

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
            "profile_id": qa_pair.profile_id,
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


class BulkUploadRequest(BaseModel):
    qa_pairs: List[QAPairCreate]
    profile_id: Optional[str] = None  # Can set at batch level


@router.post("/{user_id}/bulk-upload", response_model=List[QAPairResponse])
async def bulk_upload_qa_pairs(
    user_id: str,
    request: BulkUploadRequest,
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
                "profile_id": pair.profile_id or request.profile_id,  # Individual or batch-level
            }
            for pair in request.qa_pairs
        ]

        result = supabase.table("qa_pairs").insert(data).execute()

        if not result.data:
            raise HTTPException(status_code=400, detail="Failed to upload Q&A pairs")

        logger.info(f"Bulk uploaded {len(result.data)} Q&A pairs for user {user_id}, profile {request.profile_id}")
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


@router.post("/{user_id}/migrate-to-qdrant")
async def migrate_user_embeddings_to_qdrant(
    user_id: str,
    supabase: Client = Depends(get_supabase_client)
):
    """
    TEMPORARY: Migrate user's Q&A embeddings from Supabase to Qdrant.
    This endpoint will be removed after migration is complete.
    """
    try:
        from app.core.config import settings
        
        # Check if Qdrant is configured
        if not settings.QDRANT_URL:
            raise HTTPException(status_code=503, detail="Qdrant not configured")
        
        # Get Qdrant service
        qdrant = get_qdrant_service()
        if not qdrant:
            raise HTTPException(status_code=503, detail="Qdrant service unavailable")
        
        # Fetch Q&A pairs with embeddings from Supabase
        result = supabase.table('qa_pairs')\
            .select('*')\
            .eq('user_id', user_id)\
            .not_.is_('question_embedding', 'null')\
            .execute()
        
        qa_pairs = result.data
        
        if not qa_pairs:
            return {
                "message": "No Q&A pairs with embeddings found",
                "total": 0,
                "success": 0,
                "failed": 0
            }
        
        total = len(qa_pairs)
        logger.info(f"Starting migration of {total} Q&A pairs for user {user_id}")
        
        # Process embeddings (handle string format if needed)
        for qa in qa_pairs:
            embedding = qa.get('question_embedding')
            if isinstance(embedding, str):
                import json
                try:
                    embedding_list = json.loads(embedding)
                    qa['question_embedding'] = embedding_list
                except Exception as e:
                    logger.error(f"Error parsing embedding for {qa['id']}: {e}")
                    qa['question_embedding'] = None
        
        # Batch upload to Qdrant
        success_count, failed_count = await qdrant.batch_upsert_qa_pairs(qa_pairs)
        
        logger.info(f"Migration complete: {success_count} success, {failed_count} failed")
        
        # Get collection info
        collection_info = qdrant.get_collection_info()
        
        return {
            "message": "Migration completed",
            "total": total,
            "success": success_count,
            "failed": failed_count,
            "collection_points": collection_info.get('points_count', 0)
        }
        
    except Exception as e:
        logger.error(f"Error during migration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/qdrant-status")
async def check_qdrant_status(user_id: str):
    """
    TEMPORARY: Check Qdrant collection status and search capability
    """
    try:
        qdrant = get_qdrant_service()
        if not qdrant:
            return {"error": "Qdrant not available"}
        
        # Get collection info
        collection_info = qdrant.get_collection_info()
        
        # Try a test search
        test_results = await qdrant.search_similar_qa_pairs(
            query_text="introduce yourself",
            user_id=user_id,
            similarity_threshold=0.5,
            limit=5
        )
        
        # Scroll to see what's actually in the collection for this user
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        scroll_result = qdrant.client.scroll(
            collection_name=qdrant.COLLECTION_NAME,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            ),
            limit=10
        )
        
        points = scroll_result[0] if scroll_result else []
        
        return {
            "collection_info": collection_info,
            "test_search_results": len(test_results),
            "sample_results": [
                {
                    "id": r.get("id"),
                    "question": r.get("question", "")[:100],
                    "similarity": r.get("similarity")
                }
                for r in test_results[:3]
            ],
            "user_points_in_collection": len(points),
            "sample_points": [
                {
                    "id": str(p.id),
                    "question": p.payload.get("question", "")[:100] if p.payload else "No payload"
                }
                for p in points[:3]
            ]
        }
        
    except Exception as e:
        logger.error(f"Error checking Qdrant status: {e}", exc_info=True)
        return {"error": str(e)}
