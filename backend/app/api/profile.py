"""
REST API endpoints for user profile, STAR stories, and talking points
Supports multi-profile filtering via profile_id
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from supabase import create_client, Client
from app.core.config import settings

router = APIRouter(prefix="/api/profile", tags=["profile"])


def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


# STAR Story Models
class StarStoryCreate(BaseModel):
    title: str
    situation: str
    task: str
    action: str
    result: str
    tags: Optional[List[str]] = []
    profile_id: Optional[str] = None  # Required for multi-profile support


class StarStoryUpdate(BaseModel):
    title: Optional[str] = None
    situation: Optional[str] = None
    task: Optional[str] = None
    action: Optional[str] = None
    result: Optional[str] = None
    tags: Optional[list[str]] = None
    is_favorite: Optional[bool] = None


class StarStoryResponse(BaseModel):
    id: str
    user_id: str
    profile_id: Optional[str] = None
    title: str
    situation: str
    task: str
    action: str
    result: str
    tags: List[str]
    is_favorite: bool


# Talking Point Models
class TalkingPointCreate(BaseModel):
    category: str
    content: str
    priority: Optional[int] = 0
    profile_id: Optional[str] = None  # Required for multi-profile support


class TalkingPointUpdate(BaseModel):
    category: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[int] = None


class TalkingPointResponse(BaseModel):
    id: str
    user_id: str
    profile_id: Optional[str] = None
    category: str
    content: str
    priority: int


# STAR Stories Endpoints
@router.get("/star-stories/{user_id}")
async def get_star_stories(user_id: str, profile_id: Optional[str] = None):
    """Get all STAR stories for a user, optionally filtered by profile"""
    supabase = get_supabase()

    query = supabase.table("star_stories").select("*").eq("user_id", user_id)

    if profile_id:
        query = query.eq("profile_id", profile_id)

    response = query.execute()

    return {"stories": response.data}


@router.post("/star-stories/{user_id}")
async def create_star_story(user_id: str, story: StarStoryCreate):
    """Create a new STAR story"""
    supabase = get_supabase()

    data = {
        "user_id": user_id,
        "title": story.title,
        "situation": story.situation,
        "task": story.task,
        "action": story.action,
        "result": story.result,
        "tags": story.tags or [],
        "profile_id": story.profile_id
    }

    response = supabase.table("star_stories").insert(data).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create story")

    return {"story": response.data[0]}


@router.put("/star-stories/{story_id}")
async def update_star_story(story_id: str, story: StarStoryUpdate):
    """Update a STAR story"""
    supabase = get_supabase()

    update_data = {k: v for k, v in story.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    response = supabase.table("star_stories").update(update_data).eq("id", story_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Story not found")

    return {"story": response.data[0]}


@router.delete("/star-stories/{story_id}")
async def delete_star_story(story_id: str):
    """Delete a STAR story"""
    supabase = get_supabase()

    response = supabase.table("star_stories").delete().eq("id", story_id).execute()

    return {"message": "Story deleted successfully"}


# Talking Points Endpoints
@router.get("/talking-points/{user_id}")
async def get_talking_points(user_id: str, profile_id: Optional[str] = None):
    """Get all talking points for a user, optionally filtered by profile"""
    supabase = get_supabase()

    query = supabase.table("talking_points").select("*").eq("user_id", user_id)

    if profile_id:
        query = query.eq("profile_id", profile_id)

    response = query.order("priority", desc=True).execute()

    return {"talking_points": response.data}


@router.post("/talking-points/{user_id}")
async def create_talking_point(user_id: str, point: TalkingPointCreate):
    """Create a new talking point"""
    supabase = get_supabase()

    data = {
        "user_id": user_id,
        "category": point.category,
        "content": point.content,
        "priority": point.priority or 0,
        "profile_id": point.profile_id
    }

    response = supabase.table("talking_points").insert(data).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create talking point")

    return {"talking_point": response.data[0]}


@router.put("/talking-points/{point_id}")
async def update_talking_point(point_id: str, point: TalkingPointUpdate):
    """Update a talking point"""
    supabase = get_supabase()

    update_data = {k: v for k, v in point.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    response = supabase.table("talking_points").update(update_data).eq("id", point_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Talking point not found")

    return {"talking_point": response.data[0]}


@router.delete("/talking-points/{point_id}")
async def delete_talking_point(point_id: str):
    """Delete a talking point"""
    supabase = get_supabase()

    response = supabase.table("talking_points").delete().eq("id", point_id).execute()

    return {"message": "Talking point deleted successfully"}


# User Context Endpoint (for interview session)
@router.get("/context/{user_id}")
async def get_user_context(user_id: str, profile_id: Optional[str] = None):
    """Get all user context for interview session (stories, talking points, resume)"""
    supabase = get_supabase()

    # Get STAR stories (filtered by profile if specified)
    stories_query = supabase.table("star_stories").select("*").eq("user_id", user_id)
    if profile_id:
        stories_query = stories_query.eq("profile_id", profile_id)
    stories_response = stories_query.execute()

    # Get talking points (filtered by profile if specified)
    try:
        points_query = supabase.table("talking_points").select("*").eq("user_id", user_id)
        if profile_id:
            points_query = points_query.eq("profile_id", profile_id)
        points_response = points_query.execute()
        talking_points = points_response.data
    except Exception:
        talking_points = []

    # Get primary resume (skip if table doesn't exist or has incompatible schema)
    resume_text = ""
    try:
        resume_response = supabase.table("resumes").select("extracted_text").eq("user_id", user_id).eq("is_primary", True).execute()
        if resume_response.data and len(resume_response.data) > 0:
            resume_text = resume_response.data[0].get("extracted_text", "")
    except Exception:
        pass

    return {
        "star_stories": stories_response.data,
        "talking_points": talking_points,
        "resume_text": resume_text
    }
