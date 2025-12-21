"""
REST API endpoints for user interview profile management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from supabase import create_client, Client
from app.core.config import settings

router = APIRouter(prefix="/api/interview-profile", tags=["interview-profile"])


def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


# Pydantic Models
class InterviewProfileCreate(BaseModel):
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    projects_summary: Optional[str] = None
    technical_stack: Optional[list[str]] = []
    answer_style: Optional[str] = Field(default="balanced", pattern="^(concise|balanced|detailed)$")
    key_strengths: Optional[list[str]] = []
    custom_system_prompt: Optional[str] = None


class InterviewProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    projects_summary: Optional[str] = None
    technical_stack: Optional[list[str]] = None
    answer_style: Optional[str] = Field(default=None, pattern="^(concise|balanced|detailed)$")
    key_strengths: Optional[list[str]] = None
    custom_system_prompt: Optional[str] = None


class InterviewProfileResponse(BaseModel):
    id: str
    user_id: str
    full_name: Optional[str]
    target_role: Optional[str]
    target_company: Optional[str]
    projects_summary: Optional[str]
    technical_stack: list[str]
    answer_style: str
    key_strengths: list[str]
    custom_system_prompt: Optional[str]
    created_at: str
    updated_at: str


# Endpoints
@router.get("/{user_id}")
async def get_interview_profile(user_id: str):
    """Get user's interview profile"""
    supabase = get_supabase()

    response = supabase.table("user_interview_profiles").select("*").eq("user_id", user_id).execute()

    if not response.data or len(response.data) == 0:
        # Return default profile if none exists
        return {
            "profile": None,
            "has_profile": False
        }

    return {
        "profile": response.data[0],
        "has_profile": True
    }


@router.post("/{user_id}")
async def create_interview_profile(user_id: str, profile: InterviewProfileCreate):
    """Create a new interview profile"""
    supabase = get_supabase()

    # Check if profile already exists
    existing = supabase.table("user_interview_profiles").select("id").eq("user_id", user_id).execute()
    if existing.data and len(existing.data) > 0:
        raise HTTPException(status_code=400, detail="Profile already exists. Use PUT to update.")

    data = {
        "user_id": user_id,
        "full_name": profile.full_name,
        "target_role": profile.target_role,
        "target_company": profile.target_company,
        "projects_summary": profile.projects_summary,
        "technical_stack": profile.technical_stack or [],
        "answer_style": profile.answer_style or "balanced",
        "key_strengths": profile.key_strengths or [],
        "custom_system_prompt": profile.custom_system_prompt,
    }

    response = supabase.table("user_interview_profiles").insert(data).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create profile")

    return {"profile": response.data[0]}


@router.put("/{user_id}")
async def update_interview_profile(user_id: str, profile: InterviewProfileUpdate):
    """Update user's interview profile (upsert)"""
    supabase = get_supabase()

    # Check if profile exists
    existing = supabase.table("user_interview_profiles").select("id").eq("user_id", user_id).execute()

    update_data = {k: v for k, v in profile.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    if existing.data and len(existing.data) > 0:
        # Update existing
        response = supabase.table("user_interview_profiles").update(update_data).eq("user_id", user_id).execute()
    else:
        # Create new (upsert behavior)
        update_data["user_id"] = user_id
        if "answer_style" not in update_data:
            update_data["answer_style"] = "balanced"
        response = supabase.table("user_interview_profiles").insert(update_data).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"profile": response.data[0]}


@router.delete("/{user_id}")
async def delete_interview_profile(user_id: str):
    """Delete user's interview profile"""
    supabase = get_supabase()

    response = supabase.table("user_interview_profiles").delete().eq("user_id", user_id).execute()

    return {"message": "Profile deleted successfully"}
