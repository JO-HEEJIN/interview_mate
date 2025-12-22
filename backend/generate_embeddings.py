"""
Generate embeddings for all existing Q&A pairs
Run this script to populate question_embedding column for semantic search
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.supabase import get_supabase_client
from app.services.embedding_service import EmbeddingService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def generate_embeddings_for_user(user_id: str, batch_size: int = 10):
    """
    Generate embeddings for all Q&A pairs for a specific user

    Args:
        user_id: User ID to generate embeddings for
        batch_size: Number of Q&A pairs to process at once
    """
    try:
        supabase = get_supabase_client()
        embedding_service = EmbeddingService(supabase)

        # Get all Q&A pairs without embeddings
        result = supabase.table("qa_pairs")\
            .select("id, question")\
            .eq("user_id", user_id)\
            .is_("question_embedding", "null")\
            .execute()

        qa_pairs = result.data
        total = len(qa_pairs)

        if total == 0:
            logger.info(f"No Q&A pairs without embeddings found for user {user_id}")
            return

        logger.info(f"Found {total} Q&A pairs without embeddings for user {user_id}")

        # Process in batches
        for i in range(0, total, batch_size):
            batch = qa_pairs[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size

            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")

            for qa in batch:
                try:
                    qa_id = qa['id']
                    question = qa['question']

                    # Generate embedding
                    embedding = await embedding_service.generate_embedding(question)

                    if not embedding:
                        logger.error(f"Failed to generate embedding for Q&A {qa_id}")
                        continue

                    # Update database
                    supabase.table("qa_pairs")\
                        .update({
                            "question_embedding": embedding,
                            "embedding_model": "text-embedding-3-small"
                        })\
                        .eq("id", qa_id)\
                        .execute()

                    logger.info(f"✓ Generated embedding for: '{question[:50]}...'")

                except Exception as e:
                    logger.error(f"Error processing Q&A {qa.get('id')}: {e}")
                    continue

            # Small delay between batches to avoid rate limiting
            if i + batch_size < total:
                await asyncio.sleep(1)

        logger.info(f"✅ Completed embedding generation for {total} Q&A pairs")

    except Exception as e:
        logger.error(f"Error generating embeddings: {e}", exc_info=True)


async def generate_embeddings_all_users():
    """
    Generate embeddings for all users' Q&A pairs
    """
    try:
        supabase = get_supabase_client()

        # Get all users with Q&A pairs without embeddings
        result = supabase.table("qa_pairs")\
            .select("user_id")\
            .is_("question_embedding", "null")\
            .execute()

        if not result.data:
            logger.info("No Q&A pairs without embeddings found")
            return

        # Get unique user IDs
        user_ids = list(set(qa['user_id'] for qa in result.data))

        logger.info(f"Found {len(user_ids)} users with Q&A pairs needing embeddings")

        for user_id in user_ids:
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing user: {user_id}")
            logger.info(f"{'='*60}\n")

            await generate_embeddings_for_user(user_id)

        logger.info(f"\n{'='*60}")
        logger.info("✅ All embeddings generated successfully!")
        logger.info(f"{'='*60}\n")

    except Exception as e:
        logger.error(f"Error in batch embedding generation: {e}", exc_info=True)


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate embeddings for Q&A pairs")
    parser.add_argument("--user-id", help="Generate embeddings for specific user only")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size for processing")

    args = parser.parse_args()

    if args.user_id:
        logger.info(f"Generating embeddings for user: {args.user_id}")
        await generate_embeddings_for_user(args.user_id, args.batch_size)
    else:
        logger.info("Generating embeddings for all users")
        await generate_embeddings_all_users()


if __name__ == "__main__":
    asyncio.run(main())
