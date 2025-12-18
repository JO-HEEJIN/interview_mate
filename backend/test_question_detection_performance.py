#!/usr/bin/env python3
"""
Performance test for Pattern-based Question Detection (Phase 1.2)
Compares Claude API call (~1000ms) vs regex patterns (<1ms)
"""
import time
import asyncio
from app.services.claude import claude_service, detect_question_fast

# Test questions covering different types
test_questions = [
    # Behavioral
    "Tell me about yourself.",
    "Can you describe a time when you faced a difficult challenge?",
    "What's your greatest strength?",
    "Give me an example of when you led a team.",
    "Have you ever failed at something important?",

    # Technical
    "How would you design a URL shortener?",
    "Explain how the internet works.",
    "What are the trade-offs between SQL and NoSQL?",
    "How does caching improve performance?",

    # Situational
    "What would you do if you disagreed with your manager?",
    "How would you handle a tight deadline?",

    # General
    "Why do you want to work at OpenAI?",
    "What interests you about this role?",
    "Do you have any questions for me?",

    # Edge cases
    "This is just a statement, not a question",
    "Maybe something unclear here",
]

async def test_claude_detection(questions):
    """Test OLD method: Claude API"""
    print("[1/2] Testing OLD method (Claude API)")
    print("-" * 70)

    times = []
    for question in questions[:5]:  # Only test 5 to save API costs
        start = time.perf_counter()
        detection = await claude_service.detect_question(question)
        elapsed_ms = (time.perf_counter() - start) * 1000
        times.append(elapsed_ms)

        status = "✓" if detection["is_question"] else "✗"
        qtype = detection.get("question_type", "unknown")
        print(f"{status} [{qtype:12}] '{question[:40]:40}' - {elapsed_ms:.1f}ms")

    avg_time = sum(times) / len(times)
    print(f"\nAverage time (Claude API): {avg_time:.1f}ms")
    return avg_time

def test_fast_detection(questions):
    """Test NEW method: Pattern matching"""
    print("\n" + "=" * 70)
    print("[2/2] Testing NEW method (Pattern matching)")
    print("-" * 70)

    times = []
    for question in questions:
        start = time.perf_counter()
        detection = detect_question_fast(question)
        elapsed_ms = (time.perf_counter() - start) * 1000
        times.append(elapsed_ms)

        status = "✓" if detection["is_question"] else "✗"
        qtype = detection["question_type"]
        confidence = detection["confidence"]
        print(f"{status} [{qtype:12}] ({confidence:6}) '{question[:35]:35}' - {elapsed_ms:.4f}ms")

    avg_time = sum(times) / len(times)
    print(f"\nAverage time (Pattern matching): {avg_time:.4f}ms")
    return avg_time

async def main():
    print("=" * 70)
    print("Question Detection Performance Test (Phase 1.2 Optimization)")
    print("=" * 70)
    print(f"\nTest dataset: {len(test_questions)} questions\n")

    # Test Claude API (only 5 questions to save cost)
    claude_avg = await test_claude_detection(test_questions)

    # Test fast pattern matching (all questions)
    fast_avg = test_fast_detection(test_questions)

    # Results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Claude API average:      {claude_avg:.1f}ms")
    print(f"Pattern matching average: {fast_avg:.4f}ms")
    print(f"Speedup:                 {claude_avg / fast_avg:.0f}x faster")
    print(f"Time saved per question:  {claude_avg - fast_avg:.1f}ms")
    print(f"\n✓ Phase 1.2 optimization complete!")
    print(f"\nEstimated latency reduction in 30-min interview (15 questions):")
    print(f"  Before: {claude_avg * 15 / 1000:.1f}s total detection time")
    print(f"  After:  {fast_avg * 15 / 1000:.3f}s total detection time")
    print(f"  Saved:  {(claude_avg - fast_avg) * 15 / 1000:.1f}s ✓")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
