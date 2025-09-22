# backend/crud/match_result.py

from typing import List, Optional, Dict, Any
from .base import BaseRepository, SyncRepository
from ..models.match_result import MatchResult
from ..models.resume import Resume
from ..models.job_description import JobDescription

class MatchResultRepository(BaseRepository[MatchResult]):
    """Repository for Match Result operations with MongoDB"""
    
    def __init__(self):
        super().__init__(MatchResult)
    
    async def get_with_relations(self, id: str) -> Optional[MatchResult]:
        """Get match result with populated resume and job description"""
        return await MatchResult.get(id, fetch_links=True)
    
    async def get_by_resume_id(self, resume_id: str, skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Get all match results for a specific resume"""
        return await (MatchResult
                     .find(MatchResult.resume_id == resume_id)
                     .sort(-MatchResult.overall_score)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_by_job_id(self, job_id: str, skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Get all match results for a specific job"""
        return await (MatchResult
                     .find(MatchResult.job_description_id == job_id)
                     .sort(-MatchResult.overall_score)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_best_matches(self, min_score: float = 70.0, skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Get best match results above threshold"""
        return await (MatchResult
                     .find(MatchResult.overall_score >= min_score)
                     .sort(-MatchResult.overall_score)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_by_verdict(self, verdict: str, skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Get match results by verdict (High, Medium, Low)"""
        return await (MatchResult
                     .find(MatchResult.verdict == verdict)
                     .sort(-MatchResult.overall_score)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_bookmarked_matches(self, skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Get bookmarked match results"""
        return await (MatchResult
                     .find(MatchResult.is_bookmarked == True)
                     .sort(-MatchResult.created_at)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_by_score_range(
        self, 
        min_score: float, 
        max_score: float, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[MatchResult]:
        """Get match results within score range"""
        query = {
            "overall_score": {
                "$gte": min_score,
                "$lte": max_score
            }
        }
        return await (MatchResult
                     .find(query)
                     .sort(-MatchResult.overall_score)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def search_by_skills(self, skills: List[str], skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Search match results by matched skills"""
        query = {"matched_skills": {"$in": skills}}
        return await (MatchResult
                     .find(query)
                     .sort(-MatchResult.overall_score)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get match result statistics"""
        total_count = await MatchResult.count()
        
        # Verdict distribution
        verdict_pipeline = [
            {"$group": {"_id": "$verdict", "count": {"$sum": 1}}}
        ]
        verdict_stats = await MatchResult.aggregate(verdict_pipeline).to_list()
        verdict_distribution = {item["_id"]: item["count"] for item in verdict_stats}
        
        # Score statistics
        score_pipeline = [
            {"$group": {
                "_id": None,
                "avg_score": {"$avg": "$overall_score"},
                "min_score": {"$min": "$overall_score"},
                "max_score": {"$max": "$overall_score"},
                "avg_hard_score": {"$avg": "$hard_score"},
                "avg_soft_score": {"$avg": "$soft_score"}
            }}
        ]
        score_stats = await MatchResult.aggregate(score_pipeline).to_list(1)
        scores = score_stats[0] if score_stats else {}
        
        # Performance statistics
        performance_pipeline = [
            {"$group": {
                "_id": None,
                "avg_processing_time": {"$avg": "$processing_time_ms"},
                "min_processing_time": {"$min": "$processing_time_ms"},
                "max_processing_time": {"$max": "$processing_time_ms"}
            }}
        ]
        performance_stats = await MatchResult.aggregate(performance_pipeline).to_list(1)
        performance = performance_stats[0] if performance_stats else {}
        
        # Recent activity (last 7 days)
        from datetime import datetime, timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_query = MatchResult.find(MatchResult.created_at >= seven_days_ago)
        recent_count = await recent_query.count()
        
        # Bookmarked count
        bookmarked_query = MatchResult.find(MatchResult.is_bookmarked == True)
        bookmarked_count = await bookmarked_query.count()
        
        return {
            "total_matches": total_count,
            "recent_matches_7_days": recent_count,
            "bookmarked_matches": bookmarked_count,
            "verdict_distribution": verdict_distribution,
            "score_statistics": {
                "average_overall_score": round(scores.get("avg_score") or 0, 2),
                "minimum_score": round(scores.get("min_score") or 0, 2),
                "maximum_score": round(scores.get("max_score") or 0, 2),
                "average_hard_score": round(scores.get("avg_hard_score") or 0, 2),
                "average_soft_score": round(scores.get("avg_soft_score") or 0, 2)
            },
            "performance_statistics": {
                "average_processing_time_ms": round(performance.get("avg_processing_time") or 0, 2),
                "minimum_processing_time_ms": performance.get("min_processing_time") or 0,
                "maximum_processing_time_ms": performance.get("max_processing_time") or 0
            }
        }
    
    async def update_bookmark(self, match_id: str, is_bookmarked: bool) -> Optional[MatchResult]:
        """Update bookmark status"""
        match_result = await MatchResult.get(match_id)
        if match_result:
            match_result.is_bookmarked = is_bookmarked
            await match_result.save()
        return match_result
    
    async def update_user_rating(self, match_id: str, rating: int, notes: str = None) -> Optional[MatchResult]:
        """Update user rating and notes"""
        match_result = await MatchResult.get(match_id)
        if match_result:
            match_result.user_rating = rating
            if notes:
                match_result.user_notes = notes
            await match_result.save()
        return match_result

# Synchronous wrapper for backward compatibility
class SyncMatchResultRepository(SyncRepository[MatchResult]):
    """Synchronous MatchResult repository for backward compatibility"""
    
    def __init__(self):
        super().__init__(MatchResult)
        self.async_repo = MatchResultRepository()
    
    def get_by_resume_id(self, db, resume_id: str, skip: int = 0, limit: int = 100) -> List[MatchResult]:
        """Synchronous get_by_resume_id"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.async_repo.get_by_resume_id(resume_id, skip, limit))

# Global repository instances
match_result_repository = SyncMatchResultRepository()  # For backward compatibility
async_match_result_repository = MatchResultRepository()  # For new async code