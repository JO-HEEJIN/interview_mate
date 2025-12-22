"""
REST API endpoints for interview assistance
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.claude import get_claude_service

router = APIRouter(prefix="/api/interview", tags=["interview"])


class GenerateAnswerRequest(BaseModel):
    question: str
    resume_text: Optional[str] = ""
    star_stories: Optional[list] = []
    talking_points: Optional[list] = []


class GenerateAnswerResponse(BaseModel):
    question: str
    answer: str
    question_type: Optional[str] = None


class DetectQuestionRequest(BaseModel):
    transcription: str


class DetectQuestionResponse(BaseModel):
    is_question: bool
    question: str
    question_type: str


@router.post("/generate-answer", response_model=GenerateAnswerResponse)
async def generate_answer(request: GenerateAnswerRequest):
    """
    Generate an interview answer based on the question and user context.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    claude_service = get_claude_service()
    answer = await claude_service.generate_answer(
        question=request.question,
        resume_text=request.resume_text or "",
        star_stories=request.star_stories or [],
        talking_points=request.talking_points or []
    )

    return GenerateAnswerResponse(
        question=request.question,
        answer=answer
    )


@router.post("/detect-question", response_model=DetectQuestionResponse)
async def detect_question(request: DetectQuestionRequest):
    """
    Detect if a transcription contains an interview question.
    """
    if not request.transcription.strip():
        raise HTTPException(status_code=400, detail="Transcription cannot be empty")

    claude_service = get_claude_service()
    result = await claude_service.detect_question(request.transcription)

    return DetectQuestionResponse(
        is_question=result["is_question"],
        question=result["question"],
        question_type=result["question_type"]
    )
