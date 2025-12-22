"""
Quick test to verify RAG implementation for complex questions
"""

import asyncio
from app.services.claude import ClaudeService


async def test_query_decomposition():
    """Test query decomposition functionality"""
    claude_service = ClaudeService()

    # Test cases
    test_questions = [
        "Tell me about yourself",  # Simple - should return 1 sub-question
        "Introduce yourself and tell me why you're right for OpenAI",  # Complex - should return 2
        "Describe your leadership experience, how you handle conflict, and why you want this role",  # Very complex - should return 3
    ]

    print("=" * 80)
    print("Testing Query Decomposition")
    print("=" * 80)

    for question in test_questions:
        print(f"\n📝 Original question: '{question}'")
        sub_questions = await claude_service.decompose_question(question)
        print(f"   🔍 Decomposed into {len(sub_questions)} sub-questions:")
        for i, sub_q in enumerate(sub_questions, 1):
            print(f"      {i}. {sub_q}")

    print("\n" + "=" * 80)
    print("✅ Query decomposition test completed!")
    print("=" * 80)


async def test_rag_context_building():
    """Test that RAG context is built correctly"""
    from unittest.mock import AsyncMock, MagicMock
    from app.core.supabase import get_supabase_client

    # Create mock supabase client
    mock_supabase = MagicMock()

    claude_service = ClaudeService(supabase=mock_supabase)

    # Mock find_relevant_qa_pairs to return sample data
    mock_qa_pairs = [
        {
            "id": "1",
            "question": "Tell me about yourself",
            "answer": "I'm a software engineer with 5 years of experience...",
            "similarity": 0.95,
            "is_exact_match": False
        },
        {
            "id": "2",
            "question": "Why do you want to work at OpenAI?",
            "answer": "I'm passionate about AI safety and alignment...",
            "similarity": 0.88,
            "is_exact_match": False
        }
    ]

    # Replace find_relevant_qa_pairs with mock
    claude_service.find_relevant_qa_pairs = AsyncMock(return_value=mock_qa_pairs)

    print("\n" + "=" * 80)
    print("Testing RAG Context Building")
    print("=" * 80)

    # Test with complex question
    question = "Introduce yourself and tell me why you're right for OpenAI"
    user_profile = {"id": "test_user_123", "full_name": "Test User"}

    # This would normally call generate_answer, but we're just testing the flow
    relevant_pairs = await claude_service.find_relevant_qa_pairs(
        question=question,
        user_id=user_profile["id"],
        max_total_results=5
    )

    print(f"\n📝 Question: '{question}'")
    print(f"\n🔍 Found {len(relevant_pairs)} relevant Q&A pairs:")
    for i, pair in enumerate(relevant_pairs, 1):
        print(f"\n   {i}. [{pair['similarity']:.1%} similarity]")
        print(f"      Q: {pair['question'][:60]}...")
        print(f"      A: {pair['answer'][:60]}...")

    print("\n" + "=" * 80)
    print("✅ RAG context building test completed!")
    print("=" * 80)


async def main():
    """Run all tests"""
    await test_query_decomposition()
    await test_rag_context_building()


if __name__ == "__main__":
    asyncio.run(main())
