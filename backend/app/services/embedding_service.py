"""
Embedding Service - OpenAI Embeddings for Semantic Similarity Matching

This service handles:
- Generating embeddings for questions using OpenAI API
- Calculating cosine similarity between embedding vectors
- Caching embeddings in the database for reuse
"""

import os
import logging
from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from openai import AsyncOpenAI
from supabase import Client

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating and comparing embeddings using OpenAI API"""

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-3-small"  # 1536 dimensions, $0.02/1M tokens
        self.dimension = 1536

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text using OpenAI API

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector, or None if failed
        """
        try:
            # Clean and normalize text
            text = text.strip()
            if not text:
                logger.warning("Empty text provided for embedding")
                return None

            # Call OpenAI API
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )

            embedding = response.data[0].embedding
            logger.info(f"Generated embedding for text: {text[:50]}... (dimension: {len(embedding)})")

            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return None

    async def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts in a batch (more efficient)

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors (or None for failed items)
        """
        try:
            # Filter out empty texts but maintain indices
            valid_indices = []
            valid_texts = []
            for i, text in enumerate(texts):
                cleaned = text.strip()
                if cleaned:
                    valid_indices.append(i)
                    valid_texts.append(cleaned)

            if not valid_texts:
                logger.warning("No valid texts provided for batch embedding")
                return [None] * len(texts)

            # Call OpenAI API with batch
            response = await self.client.embeddings.create(
                model=self.model,
                input=valid_texts,
                encoding_format="float"
            )

            # Map results back to original indices
            results = [None] * len(texts)
            for i, embedding_obj in enumerate(response.data):
                original_idx = valid_indices[i]
                results[original_idx] = embedding_obj.embedding

            logger.info(f"Generated {len(valid_texts)} embeddings in batch")
            return results

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            return [None] * len(texts)

    def calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two embedding vectors

        Args:
            vec1: First embedding vector
            vec2: Second embedding vector

        Returns:
            Similarity score between 0.0 and 1.0 (1.0 = identical)
        """
        try:
            # Convert to numpy arrays
            v1 = np.array(vec1)
            v2 = np.array(vec2)

            # Calculate cosine similarity
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)

            # Clamp to [0, 1] range (should already be in [-1, 1])
            similarity = max(0.0, min(1.0, similarity))

            return float(similarity)

        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {str(e)}")
            return 0.0

    async def store_embedding(
        self,
        qa_pair_id: str,
        embedding: List[float]
    ) -> bool:
        """
        Store embedding in database for a Q&A pair

        Args:
            qa_pair_id: UUID of the Q&A pair
            embedding: Embedding vector to store

        Returns:
            True if successful, False otherwise
        """
        try:
            # Format embedding as pgvector string (no spaces after commas)
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'

            response = self.supabase.table('qa_pairs').update({
                'question_embedding': embedding_str,
                'embedding_model': self.model,
                'embedding_created_at': 'now()'
            }).eq('id', qa_pair_id).execute()

            if response.data:
                logger.info(f"Stored embedding for Q&A pair: {qa_pair_id}")
                return True
            else:
                logger.error(f"Failed to store embedding for Q&A pair: {qa_pair_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to store embedding: {str(e)}")
            return False

    async def find_similar_qa_pairs(
        self,
        user_id: str,
        query_text: str,
        similarity_threshold: float = 0.80,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find Q&A pairs semantically similar to the query text

        Args:
            user_id: User ID to search within
            query_text: Question text to find matches for
            similarity_threshold: Minimum similarity score (0.0-1.0)
            max_results: Maximum number of results to return

        Returns:
            List of matching Q&A pairs with similarity scores
        """
        try:
            # Generate embedding for query
            query_embedding = await self.generate_embedding(query_text)
            if not query_embedding:
                logger.warning("Failed to generate query embedding")
                return []

            # Format embedding as pgvector string (no spaces after commas)
            # Must match the format used when storing: [0.1,0.2,0.3] not [0.1, 0.2, 0.3]
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

            # Use the database function to find similar Q&A pairs
            response = self.supabase.rpc(
                'find_similar_qa_pairs',
                {
                    'user_id_param': user_id,
                    'query_embedding': embedding_str,
                    'similarity_threshold': similarity_threshold,
                    'max_results': max_results
                }
            ).execute()

            if response.data:
                logger.info(
                    f"Found {len(response.data)} similar Q&A pairs "
                    f"(threshold: {similarity_threshold})"
                )
                return response.data
            else:
                logger.info("No similar Q&A pairs found")
                return []

        except Exception as e:
            logger.error(f"Failed to find similar Q&A pairs: {str(e)}")
            return []

    async def get_best_match(
        self,
        user_id: str,
        query_text: str,
        similarity_threshold: float = 0.80
    ) -> Optional[Dict[str, Any]]:
        """
        Get the best matching Q&A pair for a query

        Args:
            user_id: User ID to search within
            query_text: Question text to find match for
            similarity_threshold: Minimum similarity score

        Returns:
            Best matching Q&A pair with similarity score, or None if no match
        """
        results = await self.find_similar_qa_pairs(
            user_id=user_id,
            query_text=query_text,
            similarity_threshold=similarity_threshold,
            max_results=1
        )

        if results:
            match = results[0]
            logger.info(
                f"Best match found: {match.get('question', '')[:50]}... "
                f"(similarity: {match.get('similarity', 0.0):.2f})"
            )
            return match

        logger.info("No matching Q&A pair found above threshold")
        return None

    async def update_embeddings_for_user(self, user_id: str) -> Tuple[int, int]:
        """
        Generate and store embeddings for all Q&A pairs without embeddings

        Args:
            user_id: User ID to update embeddings for

        Returns:
            Tuple of (successful_count, failed_count)
        """
        try:
            # Fetch all Q&A pairs without embeddings
            response = self.supabase.table('qa_pairs').select('*').eq(
                'user_id', user_id
            ).is_('question_embedding', 'null').execute()

            if not response.data:
                logger.info(f"No Q&A pairs need embedding updates for user: {user_id}")
                return (0, 0)

            qa_pairs = response.data
            logger.info(f"Updating embeddings for {len(qa_pairs)} Q&A pairs")

            # Generate embeddings in batch
            questions = [qa['question'] for qa in qa_pairs]
            embeddings = await self.generate_embeddings_batch(questions)

            # Store embeddings
            success_count = 0
            failed_count = 0

            for qa_pair, embedding in zip(qa_pairs, embeddings):
                if embedding:
                    success = await self.store_embedding(qa_pair['id'], embedding)
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1

            logger.info(
                f"Embedding update complete: {success_count} successful, "
                f"{failed_count} failed"
            )

            return (success_count, failed_count)

        except Exception as e:
            logger.error(f"Failed to update embeddings: {str(e)}")
            return (0, 0)


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None

def get_embedding_service(supabase: Client) -> EmbeddingService:
    """Get or create singleton embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(supabase)
    return _embedding_service
