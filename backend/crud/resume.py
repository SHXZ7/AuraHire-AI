# backend/crud/resume.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, or_
from .base import BaseRepository
from ..models.resume import Resume

class ResumeRepository(BaseRepository[Resume]):
    """Repository for Resume operations"""
    
    def __init__(self):
        super().__init__(Resume)
    
    def get_by_filename(self, db: Session, filename: str) -> Optional[Resume]:
        """Get resume by filename"""
        return db.query(Resume).filter(Resume.filename == filename).first()
    
    def search_by_skills(self, db: Session, skills: List[str], skip: int = 0, limit: int = 100) -> List[Resume]:
        """Search resumes by skills"""
        # Use JSON contains operations for PostgreSQL
        filters = []
        for skill in skills:
            filters.append(Resume.skills.op('?')(skill))
        
        return (
            db.query(Resume)
            .filter(or_(*filters))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_by_name(self, db: Session, name_pattern: str, skip: int = 0, limit: int = 100) -> List[Resume]:
        """Search resumes by candidate name"""
        return (
            db.query(Resume)
            .filter(Resume.candidate_name.ilike(f"%{name_pattern}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_experience_range(
        self, 
        db: Session, 
        min_years: int, 
        max_years: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Resume]:
        """Get resumes by experience range"""
        return (
            db.query(Resume)
            .filter(
                and_(
                    Resume.experience_years >= min_years,
                    Resume.experience_years <= max_years
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_processed_resumes(self, db: Session, skip: int = 0, limit: int = 100) -> List[Resume]:
        """Get successfully processed resumes"""
        return (
            db.query(Resume)
            .filter(Resume.is_processed == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_failed_resumes(self, db: Session, skip: int = 0, limit: int = 100) -> List[Resume]:
        """Get resumes with processing errors"""
        return (
            db.query(Resume)
            .filter(Resume.processing_error.isnot(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Get resume collection statistics"""
        total_resumes = db.query(Resume).count()
        processed_resumes = db.query(Resume).filter(Resume.is_processed == True).count()
        failed_resumes = db.query(Resume).filter(Resume.processing_error.isnot(None)).count()
        
        # Average statistics
        avg_stats = db.query(
            func.avg(Resume.experience_years).label('avg_experience'),
            func.avg(Resume.skills_count).label('avg_skills'),
            func.avg(Resume.total_words).label('avg_words')
        ).first()
        
        return {
            "total_resumes": total_resumes,
            "processed_resumes": processed_resumes,
            "failed_resumes": failed_resumes,
            "processing_success_rate": round((processed_resumes / total_resumes * 100), 2) if total_resumes > 0 else 0,
            "average_experience_years": round(avg_stats.avg_experience, 1) if avg_stats.avg_experience else 0,
            "average_skills_count": round(avg_stats.avg_skills, 1) if avg_stats.avg_skills else 0,
            "average_word_count": round(avg_stats.avg_words, 1) if avg_stats.avg_words else 0
        }
    
    def get_skill_frequency(self, db: Session, top_n: int = 20) -> List[Dict[str, Any]]:
        """Get most common skills across all resumes"""
        # This would require more complex JSON operations
        # For now, return empty list - can be implemented later with raw SQL
        return []
    
    # Async versions
    async def get_by_filename_async(self, db: AsyncSession, filename: str) -> Optional[Resume]:
        """Get resume by filename (async)"""
        from sqlalchemy import select
        result = await db.execute(select(Resume).where(Resume.filename == filename))
        return result.scalar_one_or_none()
    
    async def get_statistics_async(self, db: AsyncSession) -> Dict[str, Any]:
        """Get resume collection statistics (async)"""
        from sqlalchemy import select, func
        
        # Simplified version for async
        total_result = await db.execute(select(func.count(Resume.id)))
        total_resumes = total_result.scalar()
        
        processed_result = await db.execute(
            select(func.count(Resume.id)).where(Resume.is_processed == True)
        )
        processed_resumes = processed_result.scalar()
        
        return {
            "total_resumes": total_resumes,
            "processed_resumes": processed_resumes,
            "processing_success_rate": round((processed_resumes / total_resumes * 100), 2) if total_resumes > 0 else 0
        }

# Global repository instance
resume_repository = ResumeRepository()