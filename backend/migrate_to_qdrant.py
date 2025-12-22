"""
Migrate all Q&A embeddings from Supabase (pgvector) to Qdrant

This script:
1. Fetches all Q&A pairs with embeddings from Supabase
2. Uploads them to Qdrant in batches
3. Verifies the migration was successful

Run with: python migrate_to_qdrant.py [--user-id USER_ID]
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.supabase import get_supabase_client
from app.services.qdrant_service import QdrantService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_embeddings_to_qdrant(user_id: str = None):
    """
    Migrate embeddings from Supabase to Qdrant

    Args:
        user_id: If provided, only migrate this user's Q&A pairs
    """
    try:
        # Initialize services
        logger.info("Initializing services...")
        supabase = get_supabase_client()
        qdrant = QdrantService(
            qdrant_url=settings.QDRANT_URL,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # Build query
        query = supabase.table('qa_pairs').select('*').not_.is_('question_embedding', 'null')

        if user_id:
            query = query.eq('user_id', user_id)
            logger.info(f"Migrating Q&A pairs for user: {user_id}")
        else:
            logger.info("Migrating ALL Q&A pairs")

        # Fetch from Supabase
        result = query.execute()
        qa_pairs = result.data

        if not qa_pairs:
            logger.warning("No Q&A pairs with embeddings found")
            return

        total = len(qa_pairs)
        logger.info(f"Found {total} Q&A pairs with embeddings")

        # Process embeddings (parse if stored as string)
        for qa in qa_pairs:
            embedding = qa.get('question_embedding')
            if isinstance(embedding, str):
                # Parse string format: "[-0.014,0.024,...]"
                import json
                try:
                    # Remove brackets and split by comma
                    embedding_list = json.loads(embedding)
                    qa['question_embedding'] = embedding_list
                except Exception as e:
                    logger.error(f"Error parsing embedding for {qa['id']}: {e}")
                    qa['question_embedding'] = None

        # Upload to Qdrant in batches
        batch_size = 100
        total_success = 0
        total_failed = 0

        for i in range(0, total, batch_size):
            batch = qa_pairs[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size

            logger.info(f"Uploading batch {batch_num}/{total_batches} ({len(batch)} items)...")

            success, failed = await qdrant.batch_upsert_qa_pairs(batch)
            total_success += success
            total_failed += failed

            logger.info(f"Batch {batch_num} complete: {success} success, {failed} failed")

            # Small delay to avoid overwhelming the server
            await asyncio.sleep(0.5)

        # Verify migration
        logger.info("\n" + "="*60)
        logger.info("MIGRATION COMPLETE")
        logger.info(f"Total processed: {total}")
        logger.info(f"Successfully migrated: {total_success}")
        logger.info(f"Failed: {total_failed}")
        logger.info("="*60)

        # Get Qdrant collection info
        collection_info = qdrant.get_collection_info()
        logger.info(f"\nQdrant collection info:")
        logger.info(f"  Points count: {collection_info.get('points_count', 'unknown')}")
        logger.info(f"  Vectors count: {collection_info.get('vectors_count', 'unknown')}")
        logger.info(f"  Status: {collection_info.get('status', 'unknown')}")

        if total_failed > 0:
            logger.warning(f"\n⚠️  {total_failed} items failed to migrate. Check logs above for details.")
        else:
            logger.info("\n✅ All embeddings successfully migrated to Qdrant!")

    except Exception as e:
        logger.error(f"Error during migration: {e}", exc_info=True)
        raise


async def verify_search_works(user_id: str):
    """
    Verify that semantic search works in Qdrant

    Args:
        user_id: User ID to test with
    """
    try:
        logger.info("\n" + "="*60)
        logger.info("VERIFICATION: Testing semantic search")
        logger.info("="*60)

        qdrant = QdrantService(
            qdrant_url=settings.QDRANT_URL,
            openai_api_key=settings.OPENAI_API_KEY
        )

        # Test search
        test_query = "Tell me about yourself"
        logger.info(f"\nSearching for: '{test_query}'")

        results = await qdrant.search_similar_qa_pairs(
            query_text=test_query,
            user_id=user_id,
            similarity_threshold=0.5,  # Lower threshold for testing
            limit=3
        )

        if results:
            logger.info(f"✅ Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                logger.info(f"\n{i}. Question: {result['question'][:80]}...")
                logger.info(f"   Similarity: {result['similarity']:.4f}")
        else:
            logger.warning("⚠️  No results found. This might indicate an issue.")

    except Exception as e:
        logger.error(f"Error during verification: {e}", exc_info=True)


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate embeddings from Supabase to Qdrant")
    parser.add_argument("--user-id", help="Migrate only this user's Q&A pairs")
    parser.add_argument("--verify-only", action="store_true", help="Only run verification test")

    args = parser.parse_args()

    # Check required settings
    if not settings.QDRANT_URL:
        logger.error("QDRANT_URL not set in environment variables!")
        logger.error("Please set QDRANT_URL to your Qdrant server URL")
        return

    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set in environment variables!")
        return

    logger.info(f"Using Qdrant URL: {settings.QDRANT_URL}")

    if args.verify_only:
        if not args.user_id:
            logger.error("--verify-only requires --user-id")
            return
        await verify_search_works(args.user_id)
    else:
        # Run migration
        await migrate_embeddings_to_qdrant(args.user_id)

        # Run verification if user_id provided
        if args.user_id:
            await verify_search_works(args.user_id)


if __name__ == "__main__":
    asyncio.run(main())
