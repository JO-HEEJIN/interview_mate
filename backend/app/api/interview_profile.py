"""
REST API endpoints for user interview profile management
Supports multiple profiles per user (e.g., Google SWE, MIT PhD, F1 Visa)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from supabase import create_client, Client
from app.core.config import settings

router = APIRouter(prefix="/api/interview-profiles", tags=["interview-profiles"])

# Legacy router for backward compatibility
legacy_router = APIRouter(prefix="/api/interview-profile", tags=["interview-profile"])


def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


# Pydantic Models
class InterviewProfileCreate(BaseModel):
    profile_name: str = Field(..., min_length=1, max_length=100)
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    projects_summary: Optional[str] = None
    technical_stack: Optional[List[str]] = []
    answer_style: Optional[str] = Field(default="balanced", pattern="^(concise|balanced|detailed)$")
    key_strengths: Optional[List[str]] = []
    custom_instructions: Optional[str] = None
    is_default: Optional[bool] = False


class InterviewProfileUpdate(BaseModel):
    profile_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    target_company: Optional[str] = None
    projects_summary: Optional[str] = None
    technical_stack: Optional[List[str]] = None
    answer_style: Optional[str] = Field(default=None, pattern="^(concise|balanced|detailed)$")
    key_strengths: Optional[List[str]] = None
    custom_instructions: Optional[str] = None


class InterviewProfileResponse(BaseModel):
    id: str
    user_id: str
    profile_name: str
    full_name: Optional[str]
    target_role: Optional[str]
    target_company: Optional[str]
    projects_summary: Optional[str]
    technical_stack: List[str]
    answer_style: str
    key_strengths: List[str]
    custom_instructions: Optional[str]
    is_default: bool
    created_at: str
    updated_at: str


# ===== Multi-Profile Endpoints =====

@router.get("/{user_id}")
async def list_interview_profiles(user_id: str):
    """List all interview profiles for a user"""
    supabase = get_supabase()

    response = supabase.table("user_interview_profiles") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=False) \
        .execute()

    profiles = response.data or []

    # Find default profile
    default_profile = next((p for p in profiles if p.get("is_default")), None)
    default_profile_id = default_profile["id"] if default_profile else (profiles[0]["id"] if profiles else None)

    return {
        "profiles": profiles,
        "count": len(profiles),
        "default_profile_id": default_profile_id
    }


@router.post("/{user_id}")
async def create_interview_profile(user_id: str, profile: InterviewProfileCreate):
    """Create a new interview profile"""
    supabase = get_supabase()

    # Check if profile with same name exists
    existing = supabase.table("user_interview_profiles") \
        .select("id") \
        .eq("user_id", user_id) \
        .eq("profile_name", profile.profile_name) \
        .execute()

    if existing.data and len(existing.data) > 0:
        raise HTTPException(status_code=400, detail=f"Profile '{profile.profile_name}' already exists")

    # If this is the first profile or marked as default, handle default flag
    all_profiles = supabase.table("user_interview_profiles") \
        .select("id") \
        .eq("user_id", user_id) \
        .execute()

    is_first_profile = not all_profiles.data or len(all_profiles.data) == 0
    should_be_default = is_first_profile or profile.is_default

    # If setting this as default, unset other defaults
    if should_be_default and not is_first_profile:
        supabase.table("user_interview_profiles") \
            .update({"is_default": False}) \
            .eq("user_id", user_id) \
            .execute()

    data = {
        "user_id": user_id,
        "profile_name": profile.profile_name,
        "full_name": profile.full_name,
        "target_role": profile.target_role,
        "target_company": profile.target_company,
        "projects_summary": profile.projects_summary,
        "technical_stack": profile.technical_stack or [],
        "answer_style": profile.answer_style or "balanced",
        "key_strengths": profile.key_strengths or [],
        "custom_instructions": profile.custom_instructions,
        "is_default": should_be_default,
    }

    response = supabase.table("user_interview_profiles").insert(data).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create profile")

    return {"profile": response.data[0]}


@router.get("/{user_id}/{profile_id}")
async def get_interview_profile(user_id: str, profile_id: str):
    """Get a specific interview profile"""
    supabase = get_supabase()

    response = supabase.table("user_interview_profiles") \
        .select("*") \
        .eq("id", profile_id) \
        .eq("user_id", user_id) \
        .execute()

    if not response.data or len(response.data) == 0:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {"profile": response.data[0]}


@router.put("/{user_id}/{profile_id}")
async def update_interview_profile(user_id: str, profile_id: str, profile: InterviewProfileUpdate):
    """Update a specific interview profile"""
    supabase = get_supabase()

    # Check profile exists and belongs to user
    existing = supabase.table("user_interview_profiles") \
        .select("id, profile_name") \
        .eq("id", profile_id) \
        .eq("user_id", user_id) \
        .execute()

    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=404, detail="Profile not found")

    # If renaming, check for duplicate name
    if profile.profile_name and profile.profile_name != existing.data[0].get("profile_name"):
        duplicate = supabase.table("user_interview_profiles") \
            .select("id") \
            .eq("user_id", user_id) \
            .eq("profile_name", profile.profile_name) \
            .neq("id", profile_id) \
            .execute()

        if duplicate.data and len(duplicate.data) > 0:
            raise HTTPException(status_code=400, detail=f"Profile '{profile.profile_name}' already exists")

    update_data = {k: v for k, v in profile.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    response = supabase.table("user_interview_profiles") \
        .update(update_data) \
        .eq("id", profile_id) \
        .execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to update profile")

    return {"profile": response.data[0]}


@router.delete("/{user_id}/{profile_id}")
async def delete_interview_profile(user_id: str, profile_id: str):
    """Delete a specific interview profile"""
    supabase = get_supabase()

    # Check if this is the only profile
    all_profiles = supabase.table("user_interview_profiles") \
        .select("id, is_default") \
        .eq("user_id", user_id) \
        .execute()

    if len(all_profiles.data) <= 1:
        raise HTTPException(status_code=400, detail="Cannot delete the last profile. Create another profile first.")

    # Check if deleting default profile
    profile_to_delete = next((p for p in all_profiles.data if p["id"] == profile_id), None)

    # Delete the profile (CASCADE will delete related data)
    response = supabase.table("user_interview_profiles") \
        .delete() \
        .eq("id", profile_id) \
        .eq("user_id", user_id) \
        .execute()

    # If deleted profile was default, set another as default
    if profile_to_delete and profile_to_delete.get("is_default"):
        remaining = supabase.table("user_interview_profiles") \
            .select("id") \
            .eq("user_id", user_id) \
            .limit(1) \
            .execute()

        if remaining.data:
            supabase.table("user_interview_profiles") \
                .update({"is_default": True}) \
                .eq("id", remaining.data[0]["id"]) \
                .execute()

    return {"message": "Profile deleted successfully"}


@router.post("/{user_id}/{profile_id}/set-default")
async def set_default_profile(user_id: str, profile_id: str):
    """Set a profile as the default"""
    supabase = get_supabase()

    # Check profile exists
    existing = supabase.table("user_interview_profiles") \
        .select("id") \
        .eq("id", profile_id) \
        .eq("user_id", user_id) \
        .execute()

    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Unset all other defaults
    supabase.table("user_interview_profiles") \
        .update({"is_default": False}) \
        .eq("user_id", user_id) \
        .execute()

    # Set this profile as default
    response = supabase.table("user_interview_profiles") \
        .update({"is_default": True}) \
        .eq("id", profile_id) \
        .execute()

    return {"message": "Default profile updated", "profile": response.data[0]}


@router.post("/{user_id}/{profile_id}/duplicate")
async def duplicate_profile(user_id: str, profile_id: str, new_name: str = Query(..., min_length=1)):
    """Duplicate an existing profile with a new name"""
    supabase = get_supabase()

    # Get source profile
    source = supabase.table("user_interview_profiles") \
        .select("*") \
        .eq("id", profile_id) \
        .eq("user_id", user_id) \
        .execute()

    if not source.data or len(source.data) == 0:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Check new name doesn't exist
    existing = supabase.table("user_interview_profiles") \
        .select("id") \
        .eq("user_id", user_id) \
        .eq("profile_name", new_name) \
        .execute()

    if existing.data and len(existing.data) > 0:
        raise HTTPException(status_code=400, detail=f"Profile '{new_name}' already exists")

    # Create duplicate
    source_data = source.data[0]
    new_data = {
        "user_id": user_id,
        "profile_name": new_name,
        "full_name": source_data.get("full_name"),
        "target_role": source_data.get("target_role"),
        "target_company": source_data.get("target_company"),
        "projects_summary": source_data.get("projects_summary"),
        "technical_stack": source_data.get("technical_stack", []),
        "answer_style": source_data.get("answer_style", "balanced"),
        "key_strengths": source_data.get("key_strengths", []),
        "custom_instructions": source_data.get("custom_instructions"),
        "is_default": False,
    }

    response = supabase.table("user_interview_profiles").insert(new_data).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to duplicate profile")

    return {"profile": response.data[0]}


# ===== Legacy Endpoints (backward compatibility) =====

@legacy_router.get("/{user_id}")
async def legacy_get_profile(user_id: str):
    """Legacy: Get user's default interview profile"""
    supabase = get_supabase()

    # First try to get default profile
    response = supabase.table("user_interview_profiles") \
        .select("*") \
        .eq("user_id", user_id) \
        .eq("is_default", True) \
        .execute()

    # If no default, get any profile
    if not response.data or len(response.data) == 0:
        response = supabase.table("user_interview_profiles") \
            .select("*") \
            .eq("user_id", user_id) \
            .limit(1) \
            .execute()

    if not response.data or len(response.data) == 0:
        return {"profile": None, "has_profile": False}

    return {"profile": response.data[0], "has_profile": True}


@legacy_router.post("/{user_id}")
async def legacy_create_profile(user_id: str, profile: InterviewProfileUpdate):
    """Legacy: Create interview profile (creates as 'Default')"""
    create_data = InterviewProfileCreate(
        profile_name="Default",
        full_name=profile.full_name,
        target_role=profile.target_role,
        target_company=profile.target_company,
        projects_summary=profile.projects_summary,
        technical_stack=profile.technical_stack,
        answer_style=profile.answer_style,
        key_strengths=profile.key_strengths,
        custom_instructions=profile.custom_instructions,
        is_default=True,
    )
    return await create_interview_profile(user_id, create_data)


@legacy_router.put("/{user_id}")
async def legacy_update_profile(user_id: str, profile: InterviewProfileUpdate):
    """Legacy: Update user's default interview profile (upsert)"""
    supabase = get_supabase()

    # Find default profile
    existing = supabase.table("user_interview_profiles") \
        .select("id") \
        .eq("user_id", user_id) \
        .eq("is_default", True) \
        .execute()

    # If no default, find any profile
    if not existing.data or len(existing.data) == 0:
        existing = supabase.table("user_interview_profiles") \
            .select("id") \
            .eq("user_id", user_id) \
            .limit(1) \
            .execute()

    if existing.data and len(existing.data) > 0:
        # Update existing profile
        profile_id = existing.data[0]["id"]
        return await update_interview_profile(user_id, profile_id, profile)
    else:
        # Create new profile
        return await legacy_create_profile(user_id, profile)


@legacy_router.delete("/{user_id}")
async def legacy_delete_profile(user_id: str):
    """Legacy: Delete user's default interview profile"""
    supabase = get_supabase()

    # This deletes ALL profiles for the user (legacy behavior)
    response = supabase.table("user_interview_profiles") \
        .delete() \
        .eq("user_id", user_id) \
        .execute()

    return {"message": "Profile deleted successfully"}
