# RAG Performance Fix - Parallel Search Strategy

## Problem
1. **Long questions timeout** (300+ chars) - decomposition hangs
2. **Speed degradation** - Sequential searches take too long (5s × 3 = 15s)

## Improved Solution

### Key Insight
- Keep decomposition for compound questions (accuracy)
- Make searches parallel (speed)
- Add timeouts everywhere (no hangs)

### Strategy
1. **Decompose with timeout** (10s)
   - If timeout: Use simple heuristic split ("and", "however", "but")

2. **Parallel searches** using `asyncio.gather()`
   - Run all sub-question searches simultaneously
   - 5s × 3 sequential → 5s total (parallel)

3. **Limit to 3 sub-questions** max
   - Prevents excessive parallel load

### Speed Improvement
```
Before: Decompose(10s) + Search1(5s) + Search2(5s) + Search3(5s) = 25s
After:  Decompose(3s) + Parallel Searches(5s) + Synthesis(2s) = 10s
Improvement: 60% faster
```

---

## To-Do List

### Phase 1: Add Timeouts & Heuristic Fallback
- [x] 1. Add 10s timeout to `decompose_question()`
- [x] 2. Add heuristic fallback: split on "and", "however", "also", "but"
- [x] 3. Limit sub-questions to max 3

### Phase 2: Parallel Searches
- [x] 4. Change `find_relevant_qa_pairs()` to use `asyncio.gather()`
- [x] 5. Add error handling for individual search failures
- [x] 6. Deduplicate results from parallel searches

### Phase 3: Testing
- [ ] 7. Test short question: "Introduce yourself" (~0.5s)
- [ ] 8. Test compound: "Introduce yourself and why OpenAI" (~3s)
- [ ] 9. Test long question: The fintech CTO question (~10s)
- [ ] 10. Verify no timeouts/hangs

### Phase 4: Deploy & Cleanup
- [ ] 11. Commit and deploy to Railway
- [ ] 12. Remove `/migrate-to-qdrant` endpoint
- [ ] 13. Remove `/qdrant-status` endpoint

---

## Implementation Details

### File: `app/services/claude.py`

#### Change 1: decompose_question (line 235)

```python
import asyncio
import re

async def decompose_question(self, question: str) -> List[str]:
    """Decompose with timeout and heuristic fallback"""

    def heuristic_split(q: str) -> List[str]:
        """Simple heuristic: split on conjunctions"""
        # Split on common conjunctions
        parts = re.split(r'\s+(?:and|however|also|but)\s+', q, flags=re.IGNORECASE)
        return [p.strip() for p in parts if p.strip()]

    try:
        logger.info(f"Decomposing question ({len(question)} chars): '{question[:80]}...'")

        # Add 10s timeout
        async with asyncio.timeout(10.0):
            completion = await self.openai_client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[...],
                response_format=DecomposedQueries,
            )

            queries = completion.choices[0].message.parsed.queries

            # Limit to max 3 sub-questions
            if len(queries) > 3:
                logger.warning(f"Truncating {len(queries)} sub-questions to 3")
                queries = queries[:3]

            logger.info(f"Decomposed into {len(queries)} sub-questions")
            return queries

    except asyncio.TimeoutError:
        logger.warning("Decomposition timed out, using heuristic split")
        queries = heuristic_split(question)
        return queries[:3] if len(queries) > 3 else queries

    except Exception as e:
        logger.error(f"Decomposition failed: {e}, using heuristic")
        queries = heuristic_split(question)
        return queries[:3] if len(queries) > 3 else (queries if queries else [question])
```

#### Change 2: find_relevant_qa_pairs (line 289)

```python
async def find_relevant_qa_pairs(
    self,
    question: str,
    user_id: str,
    max_total_results: int = 5
) -> List[dict]:
    """Find relevant Q&A pairs with PARALLEL searches"""

    if not self.qdrant_service:
        return []

    try:
        # Step 1: Decompose question
        sub_questions = await self.decompose_question(question)
        logger.info(f"Searching for {len(sub_questions)} sub-questions in parallel")

        # Step 2: PARALLEL searches using asyncio.gather
        async def search_one(sub_q: str) -> List[dict]:
            """Search for one sub-question with error handling"""
            try:
                async with asyncio.timeout(5.0):
                    return await self.qdrant_service.search_similar_qa_pairs(
                        query_text=sub_q,
                        user_id=user_id,
                        similarity_threshold=0.60,
                        limit=3
                    )
            except asyncio.TimeoutError:
                logger.warning(f"Search timed out for: '{sub_q[:60]}...'")
                return []
            except Exception as e:
                logger.error(f"Search failed for '{sub_q[:60]}...': {e}")
                return []

        # Run all searches in parallel
        search_results = await asyncio.gather(
            *[search_one(sq) for sq in sub_questions]
        )

        # Step 3: Deduplicate and merge results
        all_matches = []
        seen_ids = set()

        for matches in search_results:
            for match in matches:
                # Mark high similarity as exact match
                if match.get('similarity', 0) > 0.92:
                    match['is_exact_match'] = True
                else:
                    match['is_exact_match'] = False

                # Deduplicate by ID
                if match['id'] not in seen_ids:
                    all_matches.append(match)
                    seen_ids.add(match['id'])

        # Step 4: Sort by similarity and limit
        all_matches.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        top_matches = all_matches[:max_total_results]

        logger.info(f"Found {len(top_matches)} unique matches from parallel search")
        return top_matches

    except Exception as e:
        logger.error(f"Error in find_relevant_qa_pairs: {e}", exc_info=True)
        return []
```

---

## Expected Performance

### Test Cases

| Question Type | Before | After | Improvement |
|--------------|--------|-------|-------------|
| Short + match | 0.5s | 0.5s | No change ✓ |
| Short + no match | 8s | 5s | 37% faster |
| Compound (2 parts) | 15s | 6s | 60% faster |
| Long (3+ parts) | 25s | 10s | 60% faster |

### Key Wins
✅ No timeouts/hangs (10s max decompose + 5s max search)
✅ Compound questions still get all parts answered
✅ 60% faster for complex questions
✅ Parallel searches reduce total time

---

## Review
_To be filled after testing_

**Implementation Date:** TBD
**Test Results:** TBD
**Performance:** TBD
