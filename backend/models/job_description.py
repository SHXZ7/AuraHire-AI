# backend/models/job_description.py

from typing import List, Optional
from pydantic import Field
from .base import BaseModel

class JobDescription(BaseModel):
    """Job Description model for storing parsed job data in MongoDB"""
    
    # Basic job information
    title: Optional[str] = Field(default=None, index=True)
    company: Optional[str] = Field(default=None, index=True)
    location: Optional[str] = None
    job_type: Optional[str] = None  # full-time, part-time, contract, etc.
    
    # Raw content
    raw_text: str = Field(...)
    cleaned_text: Optional[str] = None
    
    # Extracted job details
    role: Optional[str] = None  # Detected role/title
    must_have_skills: Optional[List[str]] = Field(default=[], index=True)
    nice_to_have_skills: Optional[List[str]] = Field(default=[])
    qualifications: Optional[List[str]] = Field(default=[])
    experience_required: Optional[str] = None  # e.g., "2-5 years"
    
    # Job sections
    sections: Optional[dict] = Field(default={})
    
    # Statistics
    total_characters: Optional[int] = None
    total_words: Optional[int] = None
    total_lines: Optional[int] = None
    must_have_skills_count: Optional[int] = None
    nice_to_have_skills_count: Optional[int] = None
    qualifications_count: Optional[int] = None
    
    # Processing status
    is_processed: bool = Field(default=False, index=True)
    processing_error: Optional[str] = None
    
    # Metadata
    created_by: Optional[str] = None  # For future user authentication
    job_url: Optional[str] = None  # Original job posting URL
    salary_range: Optional[str] = None  # e.g., "$80k-$120k"
    industry: Optional[str] = None
    tags: Optional[List[str]] = Field(default=[])
    notes: Optional[str] = None
    
    # Status
    is_active: bool = Field(default=True, index=True)
    
    class Settings:
        name = "job_descriptions"  # MongoDB collection name
        indexes = [
            "title",
            "company",
            "must_have_skills",
            "is_processed",
            "is_active",
            "created_at"
        ]