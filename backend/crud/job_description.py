# backend/crud/job_description.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, or_
from .base import BaseRepository
from ..models.job_description import JobDescription

class JobDescriptionRepository(BaseRepository[JobDescription]):
    """Repository for Job Description operations"""
    
    def __init__(self):
        super().__init__(JobDescription)
    
    def search_by_title(self, db: Session, title_pattern: str, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Search job descriptions by title"""
        return (
            db.query(JobDescription)
            .filter(
                or_(
                    JobDescription.title.ilike(f"%{title_pattern}%"),
                    JobDescription.role.ilike(f"%{title_pattern}%")
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_by_company(self, db: Session, company_pattern: str, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Search job descriptions by company"""
        return (
            db.query(JobDescription)
            .filter(JobDescription.company.ilike(f"%{company_pattern}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_by_location(self, db: Session, location_pattern: str, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Search job descriptions by location"""
        return (
            db.query(JobDescription)
            .filter(JobDescription.location.ilike(f"%{location_pattern}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_by_skills(self, db: Session, skills: List[str], skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Search job descriptions by required skills"""
        filters = []
        for skill in skills:
            # Search in both must_have and nice_to_have skills
            filters.append(
                or_(
                    JobDescription.must_have_skills.op('?')(skill),
                    JobDescription.nice_to_have_skills.op('?')(skill)
                )
            )
        
        return (
            db.query(JobDescription)
            .filter(or_(*filters))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_active_jobs(self, db: Session, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Get active job descriptions"""
        return (
            db.query(JobDescription)
            .filter(JobDescription.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_industry(self, db: Session, industry: str, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Get job descriptions by industry"""
        return (
            db.query(JobDescription)
            .filter(JobDescription.industry.ilike(f"%{industry}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_processed_jobs(self, db: Session, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Get successfully processed job descriptions"""
        return (
            db.query(JobDescription)
            .filter(JobDescription.is_processed == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_failed_jobs(self, db: Session, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Get job descriptions with processing errors"""
        return (
            db.query(JobDescription)
            .filter(JobDescription.processing_error.isnot(None))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Get job description collection statistics"""
        total_jobs = db.query(JobDescription).count()
        active_jobs = db.query(JobDescription).filter(JobDescription.is_active == True).count()
        processed_jobs = db.query(JobDescription).filter(JobDescription.is_processed == True).count()
        failed_jobs = db.query(JobDescription).filter(JobDescription.processing_error.isnot(None)).count()
        
        # Average statistics
        avg_stats = db.query(
            func.avg(JobDescription.must_have_skills_count).label('avg_must_have'),
            func.avg(JobDescription.nice_to_have_skills_count).label('avg_nice_to_have'),
            func.avg(JobDescription.total_words).label('avg_words')
        ).first()
        
        # Top companies and locations
        top_companies = (
            db.query(JobDescription.company, func.count(JobDescription.id).label('count'))
            .filter(JobDescription.company.isnot(None))
            .group_by(JobDescription.company)
            .order_by(func.count(JobDescription.id).desc())
            .limit(5)
            .all()
        )
        
        top_locations = (
            db.query(JobDescription.location, func.count(JobDescription.id).label('count'))
            .filter(JobDescription.location.isnot(None))
            .group_by(JobDescription.location)
            .order_by(func.count(JobDescription.id).desc())
            .limit(5)
            .all()
        )
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "processed_jobs": processed_jobs,
            "failed_jobs": failed_jobs,
            "processing_success_rate": round((processed_jobs / total_jobs * 100), 2) if total_jobs > 0 else 0,
            "average_must_have_skills": round(avg_stats.avg_must_have, 1) if avg_stats.avg_must_have else 0,
            "average_nice_to_have_skills": round(avg_stats.avg_nice_to_have, 1) if avg_stats.avg_nice_to_have else 0,
            "average_word_count": round(avg_stats.avg_words, 1) if avg_stats.avg_words else 0,
            "top_companies": [{"company": company, "count": count} for company, count in top_companies],
            "top_locations": [{"location": location, "count": count} for location, count in top_locations]
        }
    
    def get_skill_demand(self, db: Session, top_n: int = 20) -> List[Dict[str, Any]]:
        """Get most in-demand skills across all job descriptions"""
        # This would require complex JSON operations
        # For now, return empty list - can be implemented later with raw SQL
        return []
    
    # Async versions
    async def get_active_jobs_async(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Get active job descriptions (async)"""
        from sqlalchemy import select
        result = await db.execute(
            select(JobDescription)
            .where(JobDescription.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_statistics_async(self, db: AsyncSession) -> Dict[str, Any]:
        """Get job description collection statistics (async)"""
        from sqlalchemy import select, func
        
        # Simplified version for async
        total_result = await db.execute(select(func.count(JobDescription.id)))
        total_jobs = total_result.scalar()
        
        active_result = await db.execute(
            select(func.count(JobDescription.id)).where(JobDescription.is_active == True)
        )
        active_jobs = active_result.scalar()
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "activity_rate": round((active_jobs / total_jobs * 100), 2) if total_jobs > 0 else 0
        }

# Global repository instance
job_description_repository = JobDescriptionRepository()