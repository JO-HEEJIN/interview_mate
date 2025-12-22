"""
Embeddings API - Generate embeddings for Q&A pairs
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from app.core.supabase import get_supabase_client
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])


class EmbeddingGenerationResponse(BaseModel):
    message: str
    total_processed: int
    user_id: str


@router.post("/generate/{user_id}", response_model=EmbeddingGenerationResponse)
async def generate_embeddings_for_user(user_id: str, background_tasks: BackgroundTasks):
    """
    Generate embeddings for all Q&A pairs without embeddings for a user.
    Runs in background to avoid timeout.
    """
    try:
        supabase = get_supabase_client()

        # Count Q&A pairs without embeddings
        result = supabase.table("qa_pairs")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .is_("question_embedding", "null")\
            .execute()

        total = result.count or 0

        if total == 0:
            return EmbeddingGenerationResponse(
                message="All Q&A pairs already have embeddings",
                total_processed=0,
                user_id=user_id
            )

        # Add background task to generate embeddings
        background_tasks.add_task(generate_embeddings_background, user_id)

        return EmbeddingGenerationResponse(
            message=f"Started generating embeddings for {total} Q&A pairs in background",
            total_processed=total,
            user_id=user_id
        )

    except Exception as e:
        logger.error(f"Error starting embedding generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def generate_embeddings_background(user_id: str):
    """
    Background task to generate embeddings for user's Q&A pairs
    """
    try:
        supabase = get_supabase_client()
        embedding_service = get_embedding_service(supabase)

        # Get all Q&A pairs without embeddings
        result = supabase.table("qa_pairs")\
            .select("id, question")\
            .eq("user_id", user_id)\
            .is_("question_embedding", "null")\
            .execute()

        qa_pairs = result.data
        total = len(qa_pairs)

        logger.info(f"Background task: Generating embeddings for {total} Q&A pairs (user: {user_id})")

        success_count = 0
        error_count = 0

        for qa in qa_pairs:
            try:
                qa_id = qa['id']
                question = qa['question']

                # Generate embedding
                embedding = await embedding_service.generate_embedding(question)

                if not embedding:
                    logger.error(f"Failed to generate embedding for Q&A {qa_id}")
                    error_count += 1
                    continue

                # Update database
                supabase.table("qa_pairs")\
                    .update({
                        "question_embedding": embedding,
                        "embedding_model": "text-embedding-3-small"
                    })\
                    .eq("id", qa_id)\
                    .execute()

                success_count += 1
                logger.info(f"✓ [{success_count}/{total}] Generated embedding for: '{question[:50]}...'")

            except Exception as e:
                error_count += 1
                logger.error(f"Error processing Q&A {qa.get('id')}: {e}")
                continue

        logger.info(f"✅ Completed: {success_count} success, {error_count} errors out of {total} total")

    except Exception as e:
        logger.error(f"Error in background embedding generation: {e}", exc_info=True)
