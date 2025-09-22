# backend/crud/job_description.py

from typing import List, Optional, Dict, Any
from .base import BaseRepository, SyncRepository
from ..models.job_description import JobDescription

class JobDescriptionRepository(BaseRepository[JobDescription]):
    """Repository for Job Description operations with MongoDB"""
    
    def __init__(self):
        super().__init__(JobDescription)
    
    async def search_by_title(self, title_pattern: str, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Search job descriptions by title"""
        query = {
            "$or": [
                {"title": {"$regex": title_pattern, "$options": "i"}},
                {"role": {"$regex": title_pattern, "$options": "i"}}
            ]
        }
        return await JobDescription.find(query).skip(skip).limit(limit).to_list()
    
    async def search_by_company(self, company_pattern: str, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Search job descriptions by company"""
        query = {"company": {"$regex": company_pattern, "$options": "i"}}
        return await JobDescription.find(query).skip(skip).limit(limit).to_list()
    
    async def search_by_location(self, location_pattern: str, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Search job descriptions by location"""
        query = {"location": {"$regex": location_pattern, "$options": "i"}}
        return await JobDescription.find(query).skip(skip).limit(limit).to_list()
    
    async def search_by_skills(self, skills: List[str], skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Search job descriptions by required skills"""
        query = {
            "$or": [
                {"must_have_skills": {"$in": skills}},
                {"nice_to_have_skills": {"$in": skills}}
            ]
        }
        return await JobDescription.find(query).skip(skip).limit(limit).to_list()
    
    async def get_active_jobs(self, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Get active job descriptions"""
        return await JobDescription.find(JobDescription.is_active == True).skip(skip).limit(limit).to_list()
    
    async def get_by_industry(self, industry: str, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Get job descriptions by industry"""
        query = {"industry": {"$regex": industry, "$options": "i"}}
        return await JobDescription.find(query).skip(skip).limit(limit).to_list()
    
    async def get_processed_jobs(self, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Get successfully processed job descriptions"""
        return await JobDescription.find(JobDescription.is_processed == True).skip(skip).limit(limit).to_list()
    
    async def get_failed_jobs(self, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Get job descriptions with processing errors"""
        query = {"processing_error": {"$ne": None}}
        return await JobDescription.find(query).skip(skip).limit(limit).to_list()
    
    async def count_active(self) -> int:
        """Count active job descriptions"""
        active_query = JobDescription.find(JobDescription.is_active == True)
        return await active_query.count()

    async def get_statistics(self) -> Dict[str, Any]:
        """Get job description statistics"""
        total_count = await JobDescription.count()
        
        # Use find().count() method properly for filters
        active_query = JobDescription.find(JobDescription.is_active == True)
        active_count = await active_query.count()
        
        processed_query = JobDescription.find(JobDescription.is_processed == True)
        processed_count = await processed_query.count()
        
        failed_query = JobDescription.find({"processing_error": {"$ne": None}})
        failed_count = await failed_query.count()
        
        # Average statistics for processed jobs
        pipeline = [
            {"$match": {"is_processed": True}},
            {"$group": {
                "_id": None,
                "avg_must_have": {"$avg": "$must_have_skills_count"},
                "avg_nice_to_have": {"$avg": "$nice_to_have_skills_count"},
                "avg_words": {"$avg": "$total_words"}
            }}
        ]
        
        avg_stats = await JobDescription.aggregate(pipeline).to_list(1)
        averages = avg_stats[0] if avg_stats else {}
        
        # Top companies
        company_pipeline = [
            {"$match": {"company": {"$ne": None}}},
            {"$group": {"_id": "$company", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_companies = await JobDescription.aggregate(company_pipeline).to_list(5)
        
        # Top locations
        location_pipeline = [
            {"$match": {"location": {"$ne": None}}},
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_locations = await JobDescription.aggregate(location_pipeline).to_list(5)
        
        return {
            "total_jobs": total_count,
            "active_jobs": active_count,
            "processed_jobs": processed_count,
            "failed_jobs": failed_count,
            "processing_success_rate": round((processed_count / total_count * 100), 2) if total_count > 0 else 0,
            "activity_rate": round((active_count / total_count * 100), 2) if total_count > 0 else 0,
            "average_must_have_skills": round(averages.get("avg_must_have") or 0, 1),
            "average_nice_to_have_skills": round(averages.get("avg_nice_to_have") or 0, 1),
            "average_word_count": round(averages.get("avg_words") or 0, 1),
            "top_companies": [{"company": item["_id"], "count": item["count"]} for item in top_companies],
            "top_locations": [{"location": item["_id"], "count": item["count"]} for item in top_locations]
        }

# Synchronous wrapper for backward compatibility
class SyncJobDescriptionRepository(SyncRepository[JobDescription]):
    """Synchronous JobDescription repository for backward compatibility"""
    
    def __init__(self):
        super().__init__(JobDescription)
        self.async_repo = JobDescriptionRepository()
    
    def search_by_title(self, db, title_pattern: str, skip: int = 0, limit: int = 100) -> List[JobDescription]:
        """Synchronous search_by_title"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.async_repo.search_by_title(title_pattern, skip, limit))

# Global repository instances
job_description_repository = SyncJobDescriptionRepository()  # For backward compatibility
async_job_description_repository = JobDescriptionRepository()  # For new async code