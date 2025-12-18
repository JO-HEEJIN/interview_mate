#!/usr/bin/env python3
"""
Performance test for Q&A cache optimization (Phase 1.1)
Compares old O(n) method vs new O(1) hash-based lookup
"""
import time
from app.services.claude import claude_service, normalize_question, calculate_similarity

# Simulate 67 Q&A pairs from database
test_qa_pairs = [
    {
        "id": f"qa_{i}",
        "question": f"Test question number {i}",
        "answer": f"Test answer {i}",
        "question_type": "general"
    }
    for i in range(67)
]

# Add specific test questions
test_qa_pairs[0] = {
    "id": "qa_specific_1",
    "question": "Tell me about yourself.",
    "answer": "I'm Heejin Jo, a startup founder...",
    "question_type": "behavioral"
}

test_qa_pairs[1] = {
    "id": "qa_specific_2",
    "question": "What are your strengths?",
    "answer": "My key strength is building production systems...",
    "question_type": "behavioral"
}

print("=" * 70)
print("Q&A Cache Performance Test (Phase 1.1 Optimization)")
print("=" * 70)
print(f"\nTest dataset: {len(test_qa_pairs)} Q&A pairs\n")

# Test questions
test_questions = [
    "Tell me about yourself.",  # Exact match
    "Tell me about yourself",   # Similar match (no period)
    "Can you tell me about yourself?",  # Similar match (different phrasing)
    "What are your strengths?",  # Exact match
    "What are your key strengths",  # Similar match
]

print("[1/2] Testing OLD method (without index)")
print("-" * 70)

old_times = []
for question in test_questions:
    start = time.perf_counter()

    # OLD METHOD: O(n) search through all Q&A pairs
    matched_qa = claude_service.find_matching_qa_pair(question, test_qa_pairs)

    elapsed_ms = (time.perf_counter() - start) * 1000
    old_times.append(elapsed_ms)

    match_status = "✓ MATCH" if matched_qa else "✗ NO MATCH"
    print(f"{match_status}: '{question[:40]}...' - {elapsed_ms:.3f}ms")

avg_old = sum(old_times) / len(old_times)
print(f"\nAverage time (old method): {avg_old:.3f}ms")

print("\n" + "=" * 70)
print("[2/2] Testing NEW method (with index)")
print("-" * 70)

# Build index first
start_index = time.perf_counter()
claude_service.build_qa_index(test_qa_pairs)
index_build_time = (time.perf_counter() - start_index) * 1000
print(f"Index build time: {index_build_time:.3f}ms (one-time cost)\n")

new_times = []
for question in test_questions:
    start = time.perf_counter()

    # NEW METHOD: O(1) hash lookup + early exit
    matched_qa = claude_service.find_matching_qa_pair_fast(question)

    elapsed_ms = (time.perf_counter() - start) * 1000
    new_times.append(elapsed_ms)

    match_status = "✓ MATCH" if matched_qa else "✗ NO MATCH"
    print(f"{match_status}: '{question[:40]}...' - {elapsed_ms:.3f}ms")

avg_new = sum(new_times) / len(new_times)
print(f"\nAverage time (new method): {avg_new:.3f}ms")

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)
print(f"Old method average: {avg_old:.3f}ms")
print(f"New method average: {avg_new:.3f}ms")
print(f"Speedup: {avg_old / avg_new:.1f}x faster")
print(f"Time saved per lookup: {avg_old - avg_new:.3f}ms")
print(f"\n✓ Phase 1.1 optimization complete!")
print("=" * 70)
