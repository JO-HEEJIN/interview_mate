"""
Context Upload API Endpoints
Handle file uploads, text input, and context management for Q&A generation
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel

from app.core.supabase import get_supabase_client
from app.services.upload_service import upload_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/context", tags=["context-upload"])

# Pydantic models
class TextContextUpload(BaseModel):
    context_type: str  # company_info, job_posting, additional
    text_content: str

class ContextResponse(BaseModel):
    id: str
    context_type: str
    source_format: str
    file_name: Optional[str]
    extracted_text: str
    metadata: dict
    created_at: str

class UploadResponse(BaseModel):
    context_id: str
    extracted_text_preview: str
    metadata: dict

@router.post("/{user_id}/upload-resume")
async def upload_resume(
    user_id: str,
    file: UploadFile = File(...)
):
    """
    Upload PDF resume and extract text.

    Args:
        user_id: User ID
        file: PDF file to upload

    Returns:
        Context ID and extracted text preview

    Raises:
        400: Invalid file format
        500: Upload or extraction failed
    """
    logger.info(f"Resume upload requested for user {user_id}")

    try:
        # Validate PDF
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, "Only PDF files are supported for resume upload")

        # Upload and extract
        result = await upload_service.upload_resume_pdf(user_id, file)

        # Save to database
        supabase = get_supabase_client()

        context_record = {
            'user_id': user_id,
            'context_type': 'resume',
            'source_format': result['source_format'],
            'file_name': result['file_name'],
            'file_path': result['file_path'],
            'extracted_text': result['extracted_text'],
            'metadata': result['metadata']
        }

        saved = supabase.table("user_contexts").insert(context_record).execute()

        if not saved.data:
            raise HTTPException(500, "Failed to save context to database")

        logger.info(f"Successfully uploaded resume for user {user_id}")

        return {
            'context_id': saved.data[0]['id'],
            'extracted_text_preview': result['extracted_text'][:500] + "..." if len(result['extracted_text']) > 500 else result['extracted_text'],
            'metadata': result['metadata']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload failed: {e}", exc_info=True)
        raise HTTPException(500, f"Resume upload failed: {str(e)}")

@router.post("/{user_id}/upload-screenshot")
async def upload_screenshot(
    user_id: str,
    context_type: str = Form(...),  # company_info or job_posting
    file: UploadFile = File(...)
):
    """
    Upload screenshot (company info or job posting) and extract text via Vision API.

    Args:
        user_id: User ID
        context_type: Type of context ('company_info' or 'job_posting')
        file: Image file to upload

    Returns:
        Context ID and extracted text

    Raises:
        400: Invalid context type or file format
        500: Upload or extraction failed
    """
    logger.info(f"Screenshot upload requested for user {user_id}, type: {context_type}")

    try:
        # Validate context type
        if context_type not in ['company_info', 'job_posting']:
            raise HTTPException(
                400,
                "context_type must be 'company_info' or 'job_posting'"
            )

        # Validate image format
        allowed_exts = ['.jpg', '.jpeg', '.png', '.webp']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_exts):
            raise HTTPException(
                400,
                f"Only image files supported: {', '.join(allowed_exts)}"
            )

        # Upload and extract via Vision API
        result = await upload_service.upload_screenshot(user_id, file, context_type)

        # Save to database
        supabase = get_supabase_client()

        context_record = {
            'user_id': user_id,
            'context_type': context_type,
            'source_format': result['source_format'],
            'file_name': result['file_name'],
            'file_path': result['file_path'],
            'extracted_text': result['extracted_text'],
            'metadata': result['metadata']
        }

        saved = supabase.table("user_contexts").insert(context_record).execute()

        if not saved.data:
            raise HTTPException(500, "Failed to save context to database")

        logger.info(f"Successfully uploaded screenshot for user {user_id}")

        return {
            'context_id': saved.data[0]['id'],
            'extracted_text': result['extracted_text'],
            'metadata': result['metadata']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Screenshot upload failed: {e}", exc_info=True)
        raise HTTPException(500, f"Screenshot upload failed: {str(e)}")

@router.post("/{user_id}/upload-text")
async def upload_text_context(
    user_id: str,
    data: TextContextUpload
):
    """
    Upload pasted text (company info, job posting, or additional context).

    Args:
        user_id: User ID
        data: Text content and context type

    Returns:
        Context ID and extracted text

    Raises:
        400: Invalid context type or text too short
        500: Save failed
    """
    logger.info(f"Text upload requested for user {user_id}, type: {data.context_type}")

    try:
        # Validate context type
        valid_types = ['company_info', 'job_posting', 'additional']
        if data.context_type not in valid_types:
            raise HTTPException(
                400,
                f"context_type must be one of: {', '.join(valid_types)}"
            )

        # Process text
        result = await upload_service.process_text_input(
            data.text_content,
            data.context_type
        )

        # Save to database
        supabase = get_supabase_client()

        context_record = {
            'user_id': user_id,
            'context_type': data.context_type,
            'source_format': result['source_format'],
            'file_name': result['file_name'],
            'file_path': result['file_path'],
            'extracted_text': result['extracted_text'],
            'metadata': result['metadata']
        }

        saved = supabase.table("user_contexts").insert(context_record).execute()

        if not saved.data:
            raise HTTPException(500, "Failed to save context to database")

        logger.info(f"Successfully uploaded text for user {user_id}")

        return {
            'context_id': saved.data[0]['id'],
            'extracted_text': result['extracted_text']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text upload failed: {e}", exc_info=True)
        raise HTTPException(500, f"Text upload failed: {str(e)}")

@router.get("/{user_id}/contexts")
async def list_user_contexts(
    user_id: str
):
    """
    List all uploaded contexts for user.

    Args:
        user_id: User ID

    Returns:
        List of all contexts with metadata

    Raises:
        500: Database query failed
    """
    logger.info(f"Listing contexts for user {user_id}")

    try:
        supabase = get_supabase_client()

        result = supabase.table("user_contexts") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .execute()

        logger.info(f"Found {len(result.data)} contexts for user {user_id}")

        return result.data

    except Exception as e:
        logger.error(f"Failed to list contexts: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to list contexts: {str(e)}")

@router.get("/{user_id}/contexts/{context_type}")
async def get_contexts_by_type(
    user_id: str,
    context_type: str
):
    """
    Get all contexts of a specific type for user.

    Args:
        user_id: User ID
        context_type: Type of context to retrieve

    Returns:
        List of contexts matching the type

    Raises:
        400: Invalid context type
        500: Database query failed
    """
    logger.info(f"Getting {context_type} contexts for user {user_id}")

    try:
        # Validate context type
        valid_types = ['resume', 'company_info', 'job_posting', 'additional']
        if context_type not in valid_types:
            raise HTTPException(
                400,
                f"context_type must be one of: {', '.join(valid_types)}"
            )

        supabase = get_supabase_client()

        result = supabase.table("user_contexts") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("context_type", context_type) \
            .order("created_at", desc=True) \
            .execute()

        logger.info(f"Found {len(result.data)} {context_type} contexts for user {user_id}")

        return result.data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get contexts: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to get contexts: {str(e)}")

@router.delete("/contexts/{context_id}")
async def delete_context(
    context_id: str
):
    """
    Delete uploaded context.

    Args:
        context_id: Context ID to delete

    Returns:
        Success message

    Raises:
        404: Context not found
        500: Delete failed
    """
    logger.info(f"Deleting context {context_id}")

    try:
        supabase = get_supabase_client()

        result = supabase.table("user_contexts") \
            .delete() \
            .eq("id", context_id) \
            .execute()

        if not result.data:
            raise HTTPException(404, "Context not found")

        logger.info(f"Successfully deleted context {context_id}")

        return {"message": "Context deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete context: {e}", exc_info=True)
        raise HTTPException(500, f"Failed to delete context: {str(e)}")

# Note: Q&A generation endpoints will be added after qa_generation_service.py is implemented
# - POST /{user_id}/generate-qa
# - POST /{user_id}/generate-incremental
# - GET /{user_id}/generation-status/{batch_id}
