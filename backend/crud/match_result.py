# backend/crud/match_result.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, or_, desc
from .base import BaseRepository
from ..models.match_result import MatchResult
from ..models.resume import Resume
from ..models.job_description import JobDescription

class MatchResultRepository(BaseRepository[MatchResult]):
    """Repository for Match Result operations"""
    
    def __init__(self):
        super().__init__(MatchResult)
    
    def get_with_relations(self, db: Session, id: int) -> Optional[MatchResult]:
        """Get match result with resume and job description"""
        return (
            db.query(MatchResult)
            .options(joinedload(MatchResult.resume), joinedload(MatchResult.job_description))
            .filter(MatchResult.id == id)
            .first()
        )
    
    def get_by_resume_id(self, db: Session, resume_id: int, skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Get all match results for a specific resume"""
        return (
            db.query(MatchResult)
            .options(joinedload(MatchResult.job_description))
            .filter(MatchResult.resume_id == resume_id)
            .order_by(desc(MatchResult.overall_score))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_job_id(self, db: Session, job_id: int, skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Get all match results for a specific job"""
        return (
            db.query(MatchResult)
            .options(joinedload(MatchResult.resume))
            .filter(MatchResult.job_description_id == job_id)
            .order_by(desc(MatchResult.overall_score))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_best_matches(self, db: Session, min_score: float = 70.0, skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Get best match results above threshold"""
        return (
            db.query(MatchResult)
            .options(joinedload(MatchResult.resume), joinedload(MatchResult.job_description))
            .filter(MatchResult.overall_score >= min_score)
            .order_by(desc(MatchResult.overall_score))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_verdict(self, db: Session, verdict: str, skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Get match results by verdict (High, Medium, Low)"""
        return (
            db.query(MatchResult)
            .options(joinedload(MatchResult.resume), joinedload(MatchResult.job_description))
            .filter(MatchResult.verdict == verdict)
            .order_by(desc(MatchResult.overall_score))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_bookmarked_matches(self, db: Session, skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Get bookmarked match results"""
        return (
            db.query(MatchResult)
            .options(joinedload(MatchResult.resume), joinedload(MatchResult.job_description))
            .filter(MatchResult.is_bookmarked == True)
            .order_by(desc(MatchResult.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_score_range(
        self, 
        db: Session, 
        min_score: float, 
        max_score: float, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[MatchResult]:
        """Get match results within score range"""
        return (
            db.query(MatchResult)
            .options(joinedload(MatchResult.resume), joinedload(MatchResult.job_description))
            .filter(
                and_(
                    MatchResult.overall_score >= min_score,
                    MatchResult.overall_score <= max_score
                )
            )
            .order_by(desc(MatchResult.overall_score))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_by_skills(self, db: Session, skills: List[str], skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Search match results by matched skills"""
        filters = []
        for skill in skills:
            filters.append(MatchResult.matched_skills.op('?')(skill))
        
        return (
            db.query(MatchResult)
            .options(joinedload(MatchResult.resume), joinedload(MatchResult.job_description))
            .filter(or_(*filters))
            .order_by(desc(MatchResult.overall_score))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Get match result statistics"""
        total_matches = db.query(MatchResult).count()
        
        # Verdict distribution
        verdict_stats = (
            db.query(MatchResult.verdict, func.count(MatchResult.id).label('count'))
            .group_by(MatchResult.verdict)
            .all()
        )
        
        # Score statistics
        score_stats = db.query(
            func.avg(MatchResult.overall_score).label('avg_score'),
            func.min(MatchResult.overall_score).label('min_score'),
            func.max(MatchResult.overall_score).label('max_score'),
            func.avg(MatchResult.hard_score).label('avg_hard_score'),
            func.avg(MatchResult.soft_score).label('avg_soft_score')
        ).first()
        
        # Performance statistics
        performance_stats = db.query(
            func.avg(MatchResult.processing_time_ms).label('avg_processing_time'),
            func.min(MatchResult.processing_time_ms).label('min_processing_time'),
            func.max(MatchResult.processing_time_ms).label('max_processing_time')
        ).first()
        
        # Recent activity
        from datetime import datetime, timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_matches = db.query(func.count(MatchResult.id)).filter(
            MatchResult.created_at >= seven_days_ago
        ).scalar()
        
        bookmarked_count = db.query(MatchResult).filter(MatchResult.is_bookmarked == True).count()
        
        return {
            "total_matches": total_matches,
            "recent_matches_7_days": recent_matches,
            "bookmarked_matches": bookmarked_count,
            "verdict_distribution": {verdict: count for verdict, count in verdict_stats},
            "score_statistics": {
                "average_overall_score": round(score_stats.avg_score, 2) if score_stats.avg_score else 0,
                "minimum_score": round(score_stats.min_score, 2) if score_stats.min_score else 0,
                "maximum_score": round(score_stats.max_score, 2) if score_stats.max_score else 0,
                "average_hard_score": round(score_stats.avg_hard_score, 2) if score_stats.avg_hard_score else 0,
                "average_soft_score": round(score_stats.avg_soft_score, 2) if score_stats.avg_soft_score else 0
            },
            "performance_statistics": {
                "average_processing_time_ms": round(performance_stats.avg_processing_time, 2) if performance_stats.avg_processing_time else 0,
                "minimum_processing_time_ms": performance_stats.min_processing_time if performance_stats.min_processing_time else 0,
                "maximum_processing_time_ms": performance_stats.max_processing_time if performance_stats.max_processing_time else 0
            }
        }
    
    def update_bookmark(self, db: Session, match_id: int, is_bookmarked: bool) -> Optional[MatchResult]:
        """Update bookmark status"""
        match_result = self.get(db, match_id)
        if match_result:
            match_result.is_bookmarked = is_bookmarked
            db.commit()
            db.refresh(match_result)
        return match_result
    
    def update_user_rating(self, db: Session, match_id: int, rating: int, notes: str = None) -> Optional[MatchResult]:
        """Update user rating and notes"""
        match_result = self.get(db, match_id)
        if match_result:
            match_result.user_rating = rating
            if notes:
                match_result.user_notes = notes
            db.commit()
            db.refresh(match_result)
        return match_result
    
    # Async versions
    async def get_best_matches_async(
        self, 
        db: AsyncSession, 
        min_score: float = 70.0, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[MatchResult]:
        """Get best match results above threshold (async)"""
        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        result = await db.execute(
            select(MatchResult)
            .options(joinedload(MatchResult.resume), joinedload(MatchResult.job_description))
            .where(MatchResult.overall_score >= min_score)
            .order_by(desc(MatchResult.overall_score))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

# Global repository instance
match_result_repository = MatchResultRepository()