"""
Regenerate ALL embeddings for a user (clear existing and regenerate)
This ensures all embeddings use the correct format for pgvector
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.supabase import get_supabase_client
from app.services.embedding_service import EmbeddingService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def regenerate_embeddings_for_user(user_id: str):
    """
    Clear and regenerate ALL embeddings for a specific user

    Args:
        user_id: User ID to regenerate embeddings for
    """
    try:
        supabase = get_supabase_client()
        embedding_service = EmbeddingService(supabase)

        # Step 1: Count total Q&A pairs
        count_result = supabase.table("qa_pairs")\
            .select("id", count="exact")\
            .eq("user_id", user_id)\
            .execute()

        total_qa_pairs = count_result.count
        logger.info(f"Found {total_qa_pairs} Q&A pairs for user {user_id}")

        if total_qa_pairs == 0:
            logger.warning("No Q&A pairs found for this user")
            return

        # Step 2: Clear all existing embeddings
        logger.info("Clearing existing embeddings...")
        supabase.table("qa_pairs")\
            .update({"question_embedding": None})\
            .eq("user_id", user_id)\
            .execute()
        logger.info("✓ Cleared all existing embeddings")

        # Step 3: Regenerate embeddings using the service
        logger.info("Regenerating embeddings with correct format...")
        success_count, failed_count = await embedding_service.update_embeddings_for_user(user_id)

        # Step 4: Report results
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Regeneration Complete!")
        logger.info(f"   Total Q&A pairs: {total_qa_pairs}")
        logger.info(f"   Successfully generated: {success_count}")
        logger.info(f"   Failed: {failed_count}")
        logger.info(f"{'='*60}\n")

        if failed_count > 0:
            logger.warning(f"⚠️  {failed_count} embeddings failed to generate")

    except Exception as e:
        logger.error(f"Error regenerating embeddings: {e}", exc_info=True)


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Regenerate embeddings for a user")
    parser.add_argument("--user-id", required=True, help="User ID to regenerate embeddings for")

    args = parser.parse_args()

    logger.info(f"Starting embedding regeneration for user: {args.user_id}")
    await regenerate_embeddings_for_user(args.user_id)


if __name__ == "__main__":
    asyncio.run(main())
