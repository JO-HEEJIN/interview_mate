"""
Qdrant Vector Search Service
Handles all vector similarity search using Qdrant
"""

import logging
from typing import List, Dict, Optional, Tuple
from openai import AsyncOpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue
)

logger = logging.getLogger(__name__)


class QdrantService:
    """
    Service for managing Q&A embeddings in Qdrant vector database

    Benefits over pgvector:
    - No format conversion bugs (SDK handles everything)
    - 10x faster similarity search
    - Better scaling for large datasets
    - Rich filtering capabilities
    """

    COLLECTION_NAME = "qa_pairs"
    VECTOR_SIZE = 1536  # OpenAI text-embedding-3-small
    EMBEDDING_MODEL = "text-embedding-3-small"

    def __init__(self, qdrant_url: str, openai_api_key: str):
        """
        Initialize Qdrant client

        Args:
            qdrant_url: Qdrant server URL (e.g., "http://localhost:6333")
            openai_api_key: OpenAI API key for generating embeddings
        """
        self.client = QdrantClient(url=qdrant_url)
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.ensure_collection_exists()

    def ensure_collection_exists(self):
        """Create collection if it doesn't exist"""
        try:
            self.client.get_collection(self.COLLECTION_NAME)
            logger.info(f"Qdrant collection '{self.COLLECTION_NAME}' exists")
        except Exception:
            logger.info(f"Creating Qdrant collection '{self.COLLECTION_NAME}'")
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Collection '{self.COLLECTION_NAME}' created successfully")

    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text using OpenAI API

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector, or None if failed
        """
        try:
            response = await self.openai_client.embeddings.create(
                model=self.EMBEDDING_MODEL,
                input=text
            )
            embedding = response.data[0].embedding
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}", exc_info=True)
            return None

    async def upsert_qa_pair(
        self,
        qa_id: str,
        question: str,
        answer: str,
        user_id: str,
        question_type: Optional[str] = None,
        embedding: Optional[List[float]] = None
    ) -> bool:
        """
        Insert or update a Q&A pair in Qdrant

        Args:
            qa_id: UUID of Q&A pair
            question: Question text
            answer: Answer text
            user_id: User ID who owns this Q&A
            question_type: Type of question (optional)
            embedding: Pre-computed embedding (if None, will generate)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate embedding if not provided
            if embedding is None:
                embedding = await self._generate_embedding(question)
                if not embedding:
                    logger.error(f"Failed to generate embedding for Q&A {qa_id}")
                    return False

            # Upsert to Qdrant
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=qa_id,
                        vector=embedding,  # Just pass the list - no format bugs!
                        payload={
                            'question': question,
                            'answer': answer,
                            'user_id': user_id,
                            'question_type': question_type
                        }
                    )
                ]
            )

            logger.info(f"Upserted Q&A {qa_id} to Qdrant")
            return True

        except Exception as e:
            logger.error(f"Error upserting Q&A {qa_id} to Qdrant: {e}", exc_info=True)
            return False

    async def batch_upsert_qa_pairs(
        self,
        qa_pairs: List[Dict]
    ) -> Tuple[int, int]:
        """
        Batch upsert multiple Q&A pairs

        Args:
            qa_pairs: List of dicts with keys: id, question, answer, user_id, question_type, question_embedding

        Returns:
            Tuple of (success_count, failed_count)
        """
        success_count = 0
        failed_count = 0

        points = []
        for qa in qa_pairs:
            try:
                # Skip if no embedding
                if not qa.get('question_embedding'):
                    logger.warning(f"Skipping Q&A {qa['id']} - no embedding")
                    failed_count += 1
                    continue

                points.append(
                    PointStruct(
                        id=qa['id'],
                        vector=qa['question_embedding'],
                        payload={
                            'question': qa['question'],
                            'answer': qa['answer'],
                            'user_id': qa['user_id'],
                            'question_type': qa.get('question_type')
                        }
                    )
                )

            except Exception as e:
                logger.error(f"Error preparing Q&A {qa.get('id')}: {e}")
                failed_count += 1

        # Batch upload (Qdrant handles batches efficiently)
        if points:
            try:
                self.client.upsert(
                    collection_name=self.COLLECTION_NAME,
                    points=points
                )
                success_count = len(points)
                logger.info(f"Batch upserted {success_count} Q&A pairs to Qdrant")
            except Exception as e:
                logger.error(f"Error batch upserting to Qdrant: {e}", exc_info=True)
                failed_count += len(points)
                success_count = 0

        return (success_count, failed_count)

    async def delete_qa_pair(self, qa_id: str) -> bool:
        """
        Delete a Q&A pair from Qdrant

        Args:
            qa_id: UUID of Q&A pair to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete(
                collection_name=self.COLLECTION_NAME,
                points_selector=[qa_id]
            )
            logger.info(f"Deleted Q&A {qa_id} from Qdrant")
            return True

        except Exception as e:
            logger.error(f"Error deleting Q&A {qa_id} from Qdrant: {e}", exc_info=True)
            return False

    async def search_similar_qa_pairs(
        self,
        query_text: str,
        user_id: str,
        similarity_threshold: float = 0.75,
        limit: int = 5
    ) -> List[Dict]:
        """
        Search for similar Q&A pairs using semantic search

        NO MORE FORMAT BUGS! Qdrant SDK handles all serialization.

        Args:
            query_text: Question to search for
            user_id: User ID to filter by
            similarity_threshold: Minimum similarity score (0-1)
            limit: Maximum number of results

        Returns:
            List of matching Q&A pairs with similarity scores
        """
        try:
            # Generate embedding for query
            query_embedding = await self._generate_embedding(query_text)
            if not query_embedding:
                logger.warning(f"Failed to generate embedding for query: {query_text}")
                return []

            # Search in Qdrant using query_points (v1.7+ API)
            search_result = self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_embedding,  # Just pass the list!
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                ),
                limit=limit,
                score_threshold=similarity_threshold,
                with_payload=True
            )
            results = search_result.points

            # Convert to standard format
            qa_pairs = [
                {
                    'id': hit.id,
                    'question': hit.payload['question'],
                    'answer': hit.payload['answer'],
                    'question_type': hit.payload.get('question_type'),
                    'similarity': hit.score
                }
                for hit in results
            ]

            logger.info(
                f"Found {len(qa_pairs)} similar Q&A pairs for user {user_id} "
                f"(threshold: {similarity_threshold})"
            )

            return qa_pairs

        except Exception as e:
            logger.error(f"Error searching Qdrant: {e}", exc_info=True)
            return []

    def get_collection_info(self) -> Dict:
        """
        Get information about the Q&A collection

        Returns:
            Dict with collection stats
        """
        try:
            collection = self.client.get_collection(self.COLLECTION_NAME)
            return {
                'name': self.COLLECTION_NAME,
                'points_count': collection.points_count,
                'status': collection.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {
                'name': self.COLLECTION_NAME,
                'error': str(e)
            }

    async def delete_user_qa_pairs(self, user_id: str) -> int:
        """
        Delete all Q&A pairs for a user

        Args:
            user_id: User ID

        Returns:
            Number of deleted points
        """
        try:
            # Qdrant doesn't support delete by filter in old versions
            # So we scroll through and delete by IDs
            result = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                ),
                limit=10000  # Should be enough for one user
            )

            point_ids = [point.id for point in result[0]]

            if point_ids:
                self.client.delete(
                    collection_name=self.COLLECTION_NAME,
                    points_selector=point_ids
                )
                logger.info(f"Deleted {len(point_ids)} Q&A pairs for user {user_id}")

            return len(point_ids)

        except Exception as e:
            logger.error(f"Error deleting user Q&A pairs: {e}", exc_info=True)
            return 0


def get_qdrant_service(qdrant_url: str, openai_api_key: str) -> QdrantService:
    """
    Factory function to create QdrantService instance

    Args:
        qdrant_url: Qdrant server URL
        openai_api_key: OpenAI API key

    Returns:
        QdrantService instance
    """
    return QdrantService(qdrant_url, openai_api_key)
