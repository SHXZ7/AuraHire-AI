# backend/models/resume.py

from sqlalchemy import Column, String, Text, JSON, Integer, Float, Boolean
from .base import BaseModel

class Resume(BaseModel):
    """Resume model for storing parsed resume data"""
    __tablename__ = "resumes"
    
    # File information
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))  # pdf, docx, txt
    
    # Raw content
    raw_text = Column(Text, nullable=False)
    
    # Parsed personal information
    candidate_name = Column(String(255))
    emails = Column(JSON)  # List of email addresses
    phones = Column(JSON)  # List of phone numbers
    
    # Technical profile
    skills = Column(JSON)  # List of extracted skills
    experience_years = Column(Integer)
    certifications = Column(JSON)  # List of certifications
    
    # Education
    education = Column(JSON)  # List of education records
    
    # Resume sections
    sections = Column(JSON)  # Detected sections and their content
    
    # Statistics
    total_characters = Column(Integer)
    total_words = Column(Integer)
    total_lines = Column(Integer)
    skills_count = Column(Integer)
    education_count = Column(Integer)
    certifications_count = Column(Integer)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text)
    
    # Metadata
    uploaded_by = Column(String(255))  # For future user authentication
    tags = Column(JSON)  # For categorization
    notes = Column(Text)  # For user notes