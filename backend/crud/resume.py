# backend/crud/resume.py

from typing import List, Optional, Dict, Any
from .base import BaseRepository, SyncRepository
from ..models.resume import Resume

class ResumeRepository(BaseRepository[Resume]):
    """Repository for Resume operations with MongoDB"""
    
    def __init__(self):
        super().__init__(Resume)
    
    async def get_by_filename(self, filename: str) -> Optional[Resume]:
        """Get resume by filename"""
        return await Resume.find_one(Resume.filename == filename)
    
    async def search_by_skills(self, skills: List[str], skip: int = 0, limit: int = 100) -> List[Resume]:
        """Search resumes by skills"""
        # MongoDB query to find resumes that contain any of the specified skills
        query = {"skills": {"$in": skills}}
        return await Resume.find(query).skip(skip).limit(limit).to_list()
    
    async def search_by_name(self, name_pattern: str, skip: int = 0, limit: int = 100) -> List[Resume]:
        """Search resumes by candidate name"""
        # Case-insensitive regex search
        query = {"candidate_name": {"$regex": name_pattern, "$options": "i"}}
        return await Resume.find(query).skip(skip).limit(limit).to_list()
    
    async def get_by_experience_range(
        self, 
        min_years: int, 
        max_years: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Resume]:
        """Get resumes by experience range"""
        query = {
            "experience_years": {
                "$gte": min_years,
                "$lte": max_years
            }
        }
        return await Resume.find(query).skip(skip).limit(limit).to_list()
    
    async def get_processed_resumes(self, skip: int = 0, limit: int = 100) -> List[Resume]:
        """Get successfully processed resumes"""
        return await Resume.find(Resume.is_processed == True).skip(skip).limit(limit).to_list()
    
    async def get_failed_resumes(self, skip: int = 0, limit: int = 100) -> List[Resume]:
        """Get resumes with processing errors"""
        query = {"processing_error": {"$ne": None}}
        return await Resume.find(query).skip(skip).limit(limit).to_list()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get resume statistics"""
        total_count = await Resume.count()
        
        # Use find().count() method properly for filters
        processed_query = Resume.find(Resume.is_processed == True)
        processed_count = await processed_query.count()
        
        failed_query = Resume.find({"processing_error": {"$ne": None}})
        failed_count = await failed_query.count()
        
        # Average statistics for processed resumes
        pipeline = [
            {"$match": {"is_processed": True}},
            {"$group": {
                "_id": None,
                "avg_skills": {"$avg": "$skills_count"},
                "avg_experience": {"$avg": "$experience_years"},
                "avg_words": {"$avg": "$total_words"}
            }}
        ]
        
        avg_stats = await Resume.aggregate(pipeline).to_list(1)
        averages = avg_stats[0] if avg_stats else {}
        
        return {
            "total_resumes": total_count,
            "processed_resumes": processed_count,
            "failed_resumes": failed_count,
            "success_rate": round((processed_count / total_count * 100), 2) if total_count > 0 else 0,
            "average_skills_count": round(averages.get("avg_skills") or 0, 1),
            "average_experience_years": round(averages.get("avg_experience") or 0, 1),
            "average_word_count": round(averages.get("avg_words") or 0, 1)
        }

# Synchronous wrapper for backward compatibility
class SyncResumeRepository(SyncRepository[Resume]):
    """Synchronous Resume repository for backward compatibility"""
    
    def __init__(self):
        super().__init__(Resume)
        self.async_repo = ResumeRepository()
    
    def get_by_filename(self, db, filename: str) -> Optional[Resume]:
        """Synchronous get_by_filename"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.async_repo.get_by_filename(filename))

# Global repository instances
resume_repository = SyncResumeRepository()  # For backward compatibility
async_resume_repository = ResumeRepository()  # For new async code