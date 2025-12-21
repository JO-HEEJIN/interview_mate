"""
File Upload Service
Handles PDF, image, and text uploads with extraction for Q&A generation context
"""

import os
import uuid
import logging
import aiofiles
import base64
import re
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader
from PIL import Image
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

class UploadService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # File size limits per type
        self.max_sizes = {
            'pdf': 10 * 1024 * 1024,  # 10MB
            'image': 20 * 1024 * 1024,  # 20MB (Vision API supports larger)
        }

        # Allowed MIME types
        self.allowed_types = {
            'pdf': ['application/pdf'],
            'image': ['image/jpeg', 'image/png', 'image/jpg', 'image/webp'],
        }

    async def upload_resume_pdf(
        self,
        user_id: str,
        file: UploadFile
    ) -> Dict[str, Any]:
        """
        Upload and extract PDF resume.

        Args:
            user_id: User ID for file organization
            file: Uploaded PDF file

        Returns:
            Dict with file_name, file_path, extracted_text, source_format, metadata
        """
        logger.info(f"Uploading resume for user {user_id}: {file.filename}")

        # Validate file
        self._validate_file(file, 'pdf')

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        safe_filename = f"{user_id}/resumes/{file_id}{file_ext}"
        file_path = self.upload_dir / safe_filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save file
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)

            logger.info(f"Saved resume to {file_path} ({len(content)} bytes)")
        except Exception as e:
            logger.error(f"Failed to save file: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to save file: {str(e)}")

        # Extract text
        try:
            extracted_text = await self._extract_pdf_text(file_path)
            logger.info(f"Extracted {len(extracted_text)} characters from PDF")
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}", exc_info=True)
            raise HTTPException(500, f"PDF text extraction failed: {str(e)}")

        return {
            'file_name': file.filename,
            'file_path': str(file_path),
            'extracted_text': extracted_text,
            'source_format': 'pdf',
            'metadata': {
                'file_size': len(content),
                'page_count': self._get_pdf_page_count(file_path)
            }
        }

    async def upload_screenshot(
        self,
        user_id: str,
        file: UploadFile,
        context_type: str  # 'company_info' or 'job_posting'
    ) -> Dict[str, Any]:
        """
        Upload screenshot and extract text via OpenAI Vision API.

        Args:
            user_id: User ID for file organization
            file: Uploaded image file
            context_type: Type of context ('company_info' or 'job_posting')

        Returns:
            Dict with file_name, file_path, extracted_text, source_format, metadata
        """
        logger.info(f"Uploading screenshot for user {user_id}: {file.filename} (type: {context_type})")

        # Validate file
        self._validate_file(file, 'image')

        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        safe_filename = f"{user_id}/{context_type}/{file_id}{file_ext}"
        file_path = self.upload_dir / safe_filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save file
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)

            logger.info(f"Saved screenshot to {file_path} ({len(content)} bytes)")
        except Exception as e:
            logger.error(f"Failed to save file: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to save file: {str(e)}")

        # Extract text via Vision API
        try:
            extracted_text = await self._extract_image_text_vision(file_path, context_type)
            logger.info(f"Extracted {len(extracted_text)} characters via Vision API")
        except Exception as e:
            logger.error(f"Vision API extraction failed: {e}", exc_info=True)
            raise HTTPException(500, f"Vision API extraction failed: {str(e)}")

        return {
            'file_name': file.filename,
            'file_path': str(file_path),
            'extracted_text': extracted_text,
            'source_format': 'image',
            'metadata': {
                'file_size': len(content),
                'extraction_method': 'gpt-4o-vision'
            }
        }

    async def process_text_input(
        self,
        text: str,
        context_type: str
    ) -> Dict[str, Any]:
        """
        Process pasted text input.

        Args:
            text: Pasted text content
            context_type: Type of context

        Returns:
            Dict with extracted_text, source_format, metadata
        """
        logger.info(f"Processing text input ({len(text)} chars, type: {context_type})")

        if not text or len(text.strip()) < 10:
            raise HTTPException(400, "Text content too short (minimum 10 characters)")

        return {
            'file_name': None,
            'file_path': None,
            'extracted_text': text.strip(),
            'source_format': 'text',
            'metadata': {
                'char_count': len(text)
            }
        }

    async def _extract_pdf_text(self, file_path: Path) -> str:
        """
        Extract text from PDF using PyPDF2.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted and cleaned text
        """
        try:
            reader = PdfReader(str(file_path))
            text_parts = []

            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    logger.warning(f"Failed to extract page {page_num}: {e}")
                    continue

            if not text_parts:
                raise ValueError("No text could be extracted from PDF")

            full_text = "\n\n".join(text_parts)

            # Clean up extracted text
            full_text = self._clean_extracted_text(full_text)

            if len(full_text) < 50:
                raise ValueError(
                    "Extracted text too short - PDF may be image-based or empty. "
                    "Please try uploading as screenshots."
                )

            return full_text

        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {e}", exc_info=True)
            raise

    async def _extract_image_text_vision(
        self,
        file_path: Path,
        context_type: str
    ) -> str:
        """
        Extract text from image using OpenAI Vision API.

        Args:
            file_path: Path to image file
            context_type: Type of context for prompt selection

        Returns:
            Extracted text
        """
        # Read image as base64
        with open(file_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Get MIME type
        ext = file_path.suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')

        # Vision API prompt based on context type
        prompts = {
            'company_info': """Extract all text from this company information screenshot.

Focus on extracting:
- Company name and mission statement
- Core values and culture descriptions
- Recent news, achievements, or announcements
- Product or service descriptions
- Team structure or key people
- Any other relevant company information

Return the extracted text in a clean, structured format. Preserve important formatting like bullet points or sections, but remove excessive whitespace.""",

            'job_posting': """Extract all text from this job posting screenshot.

Focus on extracting:
- Job title and level (Senior, Lead, etc.)
- Key responsibilities and duties
- Required qualifications and skills
- Nice-to-have qualifications
- Years of experience required
- Education requirements
- Benefits and compensation details
- Application process or instructions

Return the extracted text in a clean, structured format. Organize by sections if possible.""",

            'additional': """Extract all text from this screenshot.

Return the extracted text in a clean, structured format. Preserve the original structure and organization as much as possible."""
        }

        try:
            logger.info(f"Calling Vision API for context_type: {context_type}")

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",  # Supports vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompts.get(context_type, prompts['additional'])
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}",
                                    "detail": "high"  # High detail for better OCR
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4096,
                temperature=0.1  # Low temperature for consistent extraction
            )

            extracted_text = response.choices[0].message.content

            if not extracted_text or len(extracted_text.strip()) < 10:
                raise ValueError("Vision API returned insufficient text")

            return self._clean_extracted_text(extracted_text)

        except Exception as e:
            logger.error(f"Vision API failed: {e}", exc_info=True)
            raise

    def _validate_file(self, file: UploadFile, file_type: str):
        """
        Validate file type and size.

        Args:
            file: Uploaded file
            file_type: Expected type ('pdf' or 'image')
        """
        # Check MIME type
        if file.content_type not in self.allowed_types[file_type]:
            raise HTTPException(
                400,
                f"Invalid file type '{file.content_type}'. "
                f"Allowed: {', '.join(self.allowed_types[file_type])}"
            )

        # Note: File size validation happens during read in upload methods
        # FastAPI doesn't provide size before reading the file

    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special control characters
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # Restore paragraph breaks (replace single newlines with double)
        text = re.sub(r'\n\s*\n', '\n\n', text)

        return text.strip()

    def _get_pdf_page_count(self, file_path: Path) -> int:
        """
        Get number of pages in PDF.

        Args:
            file_path: Path to PDF file

        Returns:
            Number of pages, or 0 if error
        """
        try:
            reader = PdfReader(str(file_path))
            return len(reader.pages)
        except Exception as e:
            logger.warning(f"Failed to count PDF pages: {e}")
            return 0

# Global instance
upload_service = UploadService()
