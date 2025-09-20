# backend/crud/__init__.py

from .resume import ResumeRepository, resume_repository
from .job_description import JobDescriptionRepository, job_description_repository
from .match_result import MatchResultRepository, match_result_repository
from .audit_log import AuditLogRepository, audit_log_repository

__all__ = [
    "ResumeRepository", 
    "JobDescriptionRepository", 
    "MatchResultRepository", 
    "AuditLogRepository",
    "resume_repository",
    "job_description_repository", 
    "match_result_repository", 
    "audit_log_repository"
]