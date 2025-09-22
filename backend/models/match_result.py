# backend/models/match_result.py

from typing import List, Optional
from pydantic import Field
from bson import ObjectId
from .base import BaseModel

class MatchResult(BaseModel):
    """Match Result model for storing resume-job matching results in MongoDB"""
    
    # Foreign keys (ObjectId references)
    resume_id: ObjectId = Field(..., index=True)
    job_description_id: ObjectId = Field(..., index=True)
    
    # Matching scores
    overall_score: float = Field(..., index=True)  # Final weighted score
    hard_score: float = Field(...)     # Skill match percentage
    soft_score: float = Field(...)     # Semantic similarity score
    verdict: str = Field(..., index=True)   # High, Medium, Low
    
    # Scoring configuration
    hard_weight: float = Field(default=0.7)       # Weight for hard skills
    soft_weight: float = Field(default=0.3)       # Weight for soft match
    
    # Skill analysis
    matched_skills: Optional[List[str]] = Field(default=[])
    missing_skills: Optional[List[str]] = Field(default=[])
    extracted_resume_skills: Optional[List[str]] = Field(default=[])
    common_keywords: Optional[List[str]] = Field(default=[])
    
    # Feedback and recommendations
    feedback: Optional[str] = None
    recommendations: Optional[List[str]] = Field(default=[])
    
    # Matching metadata
    algorithm_version: Optional[str] = None
    processing_time_ms: Optional[int] = None
    
    # Additional analysis
    skill_gap_analysis: Optional[dict] = Field(default={})
    improvement_suggestions: Optional[List[str]] = Field(default=[])
    confidence_level: Optional[float] = None  # Algorithm confidence (0-1)
    
    # Status and flags
    is_bookmarked: bool = Field(default=False)
    user_rating: Optional[int] = Field(default=None, ge=1, le=5)  # 1-5 stars
    user_notes: Optional[str] = None
    
    # Audit trail
    matched_by: Optional[str] = None  # For future user authentication
    match_context: Optional[str] = None  # web_upload, api_call, batch_process
    
    class Settings:
        name = "match_results"  # MongoDB collection name
        indexes = [
            "resume_id",
            "job_description_id",
            "overall_score",
            "verdict",
            "created_at",
            [("resume_id", 1), ("job_description_id", 1)]  # Compound index
        ]