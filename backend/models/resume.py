# backend/models/resume.py

from typing import List, Optional
from pydantic import Field
from .base import BaseModel

class Resume(BaseModel):
    """Resume model for storing parsed resume data in MongoDB"""
    
    # File information
    filename: str = Field(..., index=True)
    file_size: Optional[int] = None
    file_type: Optional[str] = None  # pdf, docx, txt
    
    # Raw content
    raw_text: str = Field(...)
    
    # Parsed personal information
    candidate_name: Optional[str] = Field(default=None, index=True)
    emails: Optional[List[str]] = Field(default=[])
    phones: Optional[List[str]] = Field(default=[])
    
    # Technical profile
    skills: Optional[List[str]] = Field(default=[], index=True)
    experience_years: Optional[int] = None
    certifications: Optional[List[str]] = Field(default=[])
    
    # Education
    education: Optional[List[dict]] = Field(default=[])
    
    # Resume sections
    sections: Optional[dict] = Field(default={})
    
    # Statistics
    total_characters: Optional[int] = None
    total_words: Optional[int] = None
    total_lines: Optional[int] = None
    skills_count: Optional[int] = None
    education_count: Optional[int] = None
    certifications_count: Optional[int] = None
    
    # Processing status
    is_processed: bool = Field(default=False, index=True)
    processing_error: Optional[str] = None
    
    # Metadata
    uploaded_by: Optional[str] = None  # For future user authentication
    tags: Optional[List[str]] = Field(default=[])
    notes: Optional[str] = None
    
    class Settings:
        name = "resumes"  # MongoDB collection name
        indexes = [
            "filename",
            "candidate_name", 
            "skills",
            "is_processed",
            "created_at"
        ]