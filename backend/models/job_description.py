# backend/models/job_description.py

from sqlalchemy import Column, String, Text, JSON, Integer, Boolean
from .base import BaseModel

class JobDescription(BaseModel):
    """Job Description model for storing parsed job data"""
    __tablename__ = "job_descriptions"
    
    # Basic job information
    title = Column(String(255))
    company = Column(String(255))
    location = Column(String(255))
    job_type = Column(String(50))  # full-time, part-time, contract, etc.
    
    # Raw content
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text)
    
    # Extracted job details
    role = Column(String(255))  # Detected role/title
    must_have_skills = Column(JSON)  # Required skills
    nice_to_have_skills = Column(JSON)  # Preferred skills
    qualifications = Column(JSON)  # Education/certification requirements
    experience_required = Column(String(100))  # e.g., "2-5 years"
    
    # Job sections
    sections = Column(JSON)  # requirements, responsibilities, benefits, etc.
    
    # Statistics
    total_characters = Column(Integer)
    total_words = Column(Integer)
    total_lines = Column(Integer)
    must_have_skills_count = Column(Integer)
    nice_to_have_skills_count = Column(Integer)
    qualifications_count = Column(Integer)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text)
    
    # Metadata
    created_by = Column(String(255))  # For future user authentication
    job_url = Column(String(500))  # Original job posting URL
    salary_range = Column(String(100))  # e.g., "$80k-$120k"
    industry = Column(String(100))
    tags = Column(JSON)  # For categorization
    notes = Column(Text)  # For user notes
    
    # Status
    is_active = Column(Boolean, default=True)  # Whether job is still open