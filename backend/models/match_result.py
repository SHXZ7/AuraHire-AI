# backend/models/match_result.py

from sqlalchemy import Column, String, Text, JSON, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class MatchResult(BaseModel):
    """Match Result model for storing resume-job matching results"""
    __tablename__ = "match_results"
    
    # Foreign keys
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    
    # Relationships
    resume = relationship("Resume", backref="match_results")
    job_description = relationship("JobDescription", backref="match_results")
    
    # Matching scores
    overall_score = Column(Float, nullable=False)  # Final weighted score
    hard_score = Column(Float, nullable=False)     # Skill match percentage
    soft_score = Column(Float, nullable=False)     # Semantic similarity score
    verdict = Column(String(50), nullable=False)   # High, Medium, Low
    
    # Scoring configuration
    hard_weight = Column(Float, default=0.7)       # Weight for hard skills
    soft_weight = Column(Float, default=0.3)       # Weight for soft match
    
    # Skill analysis
    matched_skills = Column(JSON)                  # Skills that matched
    missing_skills = Column(JSON)                  # Skills missing from resume
    extracted_resume_skills = Column(JSON)        # All skills found in resume
    common_keywords = Column(JSON)                # Common keywords between texts
    
    # Feedback and recommendations
    feedback = Column(Text)                       # Actionable feedback
    recommendations = Column(JSON)               # Structured recommendations
    
    # Matching metadata
    algorithm_version = Column(String(50))        # For tracking algorithm changes
    processing_time_ms = Column(Integer)          # Performance tracking
    
    # Additional analysis
    skill_gap_analysis = Column(JSON)             # Detailed skill gap breakdown
    improvement_suggestions = Column(JSON)       # Specific improvement areas
    confidence_level = Column(Float)             # Algorithm confidence (0-1)
    
    # Status and flags
    is_bookmarked = Column(Boolean, default=False) # User bookmarking
    user_rating = Column(Integer)                 # User feedback (1-5 stars)
    user_notes = Column(Text)                    # User's personal notes
    
    # Audit trail
    matched_by = Column(String(255))             # For future user authentication
    match_context = Column(String(100))         # web_upload, api_call, batch_process