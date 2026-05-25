"""
Background Extraction Service

Powers the AI Background Generation modal on the Profiles page (see
diary_v2.md § 2.3). Takes a resume file (PDF / md / docx) + required
organization context + required interview details, and streams a
plain-text background summary back to the frontend via Server-Sent
Events.

Distinct from qa_generation_service:
  - Output is a single plain-text summary, not 30+ Q&A pairs
  - Streaming (token-by-token via Claude messages.stream) so the user
    sees the textarea fill in as it's being written
  - No persistence to user_subscriptions / qa_pairs — the result is
    handed back to the client which writes it into
    user_interview_profiles.projects_summary via the existing update
    endpoint (auto-save picks it up)
"""

import io
import json
import logging
from pathlib import Path
from typing import AsyncIterator

import docx2txt
from anthropic import AsyncAnthropic
from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader

from app.core.config import settings

logger = logging.getLogger(__name__)

# Hard cap on raw input text per source. Resumes longer than 50k chars
# are unusual (~10+ pages); org/interview > 20k is almost always paste-bombing.
MAX_RESUME_CHARS = 50_000
MAX_CONTEXT_CHARS = 20_000

# Output budget — system prompt + a soft length cue. Per diary_v2 + the
# car_wash dilution lesson: longer prompts/outputs hurt structured
# reasoning. 500 words ≈ 3000-3500 chars, fits the widened textarea
# without scroll, leaves room in the answer-generation system prompt.
TARGET_WORD_COUNT = 500

# Claude model — re-use the same one answer generation uses (memory.md)
CLAUDE_MODEL = "claude-sonnet-4-6"


# Module-level singleton AsyncAnthropic client (per learning_log rule 3.8 —
# don't construct SDK clients per-request).
_anthropic_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client


def _extract_resume_text(file: UploadFile, raw_bytes: bytes) -> str:
    """
    Pull plain text out of a PDF / md / docx upload.
    Errors bubble as HTTPException(400) — caller surfaces them to the user.
    """
    filename = (file.filename or "").lower()
    suffix = Path(filename).suffix

    try:
        if suffix == ".pdf":
            reader = PdfReader(io.BytesIO(raw_bytes))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        elif suffix == ".md":
            # markdown is already plain text for our purposes — the LLM
            # doesn't need # headers stripped, it'll handle them.
            text = raw_bytes.decode("utf-8", errors="replace")
        elif suffix == ".docx":
            text = docx2txt.process(io.BytesIO(raw_bytes)) or ""
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{suffix}'. Use .pdf, .md, or .docx.",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to parse {suffix} upload: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Could not parse file: {e}")

    text = text.strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file has no extractable text (might be image-only PDF).",
        )

    # Cap absurdly long resumes so we don't bloat the prompt
    if len(text) > MAX_RESUME_CHARS:
        text = text[:MAX_RESUME_CHARS] + "\n\n[truncated — original exceeded character limit]"

    return text


def _build_prompt(resume_text: str, org_text: str, interview_text: str) -> str:
    """
    Construct the user message that asks Claude to extract a plain-text
    background summary.
    """
    return f"""You are extracting a CONCISE, PLAIN-TEXT background summary from a user's
resume + organization context + interview details, for an interview-prep tool.

OUTPUT RULES (these matter — non-negotiable):
  • Plain text only. NO markdown. No #, no **bold**, no - bullets, no tables.
  • Use short paragraphs separated by blank lines.
  • Target roughly {TARGET_WORD_COUNT} words. Tighter is fine; do not exceed by much.
  • Write in the user's voice ("I built X", "I led Y") — first person.
  • Structure each major achievement as Situation → Task → Action → Result, but
    written as natural prose (NOT labeled "Situation:" etc.).
  • Mention concrete metrics where the resume has them (numbers, scale, time).
  • Tailor the emphasis to the ORGANIZATION and INTERVIEW DETAILS — drop
    experiences irrelevant to the target role, surface the ones that fit.
  • End with a 1-2 sentence "what I bring to this role" close.

INPUTS:

== RESUME ==
{resume_text}

== ORGANIZATION ==
{org_text[:MAX_CONTEXT_CHARS]}

== INTERVIEW DETAILS ==
{interview_text[:MAX_CONTEXT_CHARS]}

Now write the background summary. Plain text. No preamble like "Here is the summary:" —
just start with the content."""


async def stream_background_extraction(
    file: UploadFile,
    organization_text: str,
    interview_text: str,
) -> AsyncIterator[str]:
    """
    Async generator yielding Server-Sent Events strings (data: ...\\n\\n)
    for the FastAPI StreamingResponse.

    Event payload shape:
      {"type": "text", "delta": "<chunk>"}     — partial text token(s)
      {"type": "done"}                          — stream completed cleanly
      {"type": "error", "message": "<msg>"}     — fatal error mid-stream
    """
    if not settings.ANTHROPIC_API_KEY:
        yield f"data: {json.dumps({'type': 'error', 'message': 'Anthropic API key not configured'})}\n\n"
        return

    # Read + parse the file. _extract_resume_text raises HTTPException on bad
    # input; catch it so the stream surfaces the message instead of dying mid-event.
    raw_bytes = await file.read()
    try:
        resume_text = _extract_resume_text(file, raw_bytes)
    except HTTPException as e:
        yield f"data: {json.dumps({'type': 'error', 'message': e.detail})}\n\n"
        return

    prompt = _build_prompt(resume_text, organization_text, interview_text)

    client = _get_client()
    try:
        async with client.messages.stream(
            model=CLAUDE_MODEL,
            max_tokens=1500,  # ~500 words + headroom
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text_chunk in stream.text_stream:
                if not text_chunk:
                    continue
                yield f"data: {json.dumps({'type': 'text', 'delta': text_chunk})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        logger.error(f"Claude streaming failed: {e}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


# Module-level singleton instance — mirrors qa_generation_service.py convention
background_extraction_service = None  # actual binding via lazy init below


def get_background_extraction_service():
    """Lazy accessor (kept consistent with how other services are imported)."""
    return {
        "stream": stream_background_extraction,
    }
