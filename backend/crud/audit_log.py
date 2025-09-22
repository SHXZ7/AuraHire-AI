# backend/crud/audit_log.py

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from .base import BaseRepository, SyncRepository
from ..models.audit_log import AuditLog

class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for Audit Log operations with MongoDB"""
    
    def __init__(self):
        super().__init__(AuditLog)
    
    async def log_event(
        self,
        event_type: str,
        event_action: str,
        resource_type: str = None,
        resource_id: str = None,
        user_id: str = None,
        session_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        endpoint: str = None,
        http_method: str = None,
        request_params: Dict = None,
        response_status: int = None,
        response_time_ms: int = None,
        error_message: str = None,
        business_event: str = None,
        correlation_id: str = None,
        **additional_data
    ) -> AuditLog:
        """Log a new audit event"""
        
        log_data = {
            "event_type": event_type,
            "event_action": event_action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "session_id": session_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "endpoint": endpoint,
            "http_method": http_method,
            "request_params": request_params,
            "response_status": response_status,
            "response_time_ms": response_time_ms,
            "error_message": error_message,
            "business_event": business_event,
            "correlation_id": correlation_id,
            "event_timestamp": datetime.utcnow()
        }
        
        # Add any additional data
        for key, value in additional_data.items():
            log_data[key] = value
        
        audit_log = AuditLog(**log_data)
        await audit_log.save()
        return audit_log
    
    async def get_by_event_type(self, event_type: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by event type"""
        return await (AuditLog
                     .find(AuditLog.event_type == event_type)
                     .sort(-AuditLog.event_timestamp)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_by_resource(self, resource_type: str, resource_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific resource"""
        query = {
            "resource_type": resource_type,
            "resource_id": resource_id
        }
        return await (AuditLog
                     .find(query)
                     .sort(-AuditLog.event_timestamp)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific user"""
        return await (AuditLog
                     .find(AuditLog.user_id == user_id)
                     .sort(-AuditLog.event_timestamp)
                     .skip(skip)
                     .limit(limit))
    
    async def get_by_session(self, session_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific session"""
        return await (AuditLog
                     .find(AuditLog.session_id == session_id)
                     .sort(-AuditLog.event_timestamp)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_by_correlation(self, correlation_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get related audit logs by correlation ID"""
        return await (AuditLog
                     .find(AuditLog.correlation_id == correlation_id)
                     .sort(AuditLog.event_timestamp)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs within date range"""
        query = {
            "event_timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        return await (AuditLog
                     .find(query)
                     .sort(-AuditLog.event_timestamp)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_errors(self, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs with errors"""
        query = {"error_message": {"$ne": None}}
        return await (AuditLog
                     .find(query)
                     .sort(-AuditLog.event_timestamp)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_slow_requests(self, min_time_ms: int = 1000, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for slow requests"""
        query = {"response_time_ms": {"$gte": min_time_ms}}
        return await (AuditLog
                     .find(query)
                     .sort(-AuditLog.response_time_ms)
                     .skip(skip)
                     .limit(limit)
                     .to_list())
    
    async def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get audit log statistics for the last N days"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Total events
        events_query = AuditLog.find(AuditLog.event_timestamp >= since_date)
        total_events = await events_query.count()
        
        # Event type distribution
        event_type_pipeline = [
            {"$match": {"event_timestamp": {"$gte": since_date}}},
            {"$group": {"_id": "$event_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        event_types = await AuditLog.aggregate(event_type_pipeline).to_list()
        
        # Response status distribution
        status_pipeline = [
            {"$match": {
                "event_timestamp": {"$gte": since_date},
                "response_status": {"$ne": None}
            }},
            {"$group": {"_id": "$response_status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_codes = await AuditLog.aggregate(status_pipeline).to_list()
        
        # Error count
        error_query = AuditLog.find({
            "event_timestamp": {"$gte": since_date},
            "error_message": {"$ne": None}})
        error_count = await error_query.count()
        
        # Performance statistics
        performance_pipeline = [
            {"$match": {
                "event_timestamp": {"$gte": since_date},
                "response_time_ms": {"$ne": None}
            }},
            {"$group": {
                "_id": None,
                "avg_response_time": {"$avg": "$response_time_ms"},
                "min_response_time": {"$min": "$response_time_ms"},
                "max_response_time": {"$max": "$response_time_ms"}
            }}
        ]
        performance_stats = await AuditLog.aggregate(performance_pipeline).to_list(1)
        performance = performance_stats[0] if performance_stats else {}
        
        # Active users/sessions
        unique_users_pipeline = [
            {"$match": {
                "event_timestamp": {"$gte": since_date},
                "user_id": {"$ne": None}
            }},
            {"$group": {"_id": "$user_id"}},
            {"$count": "unique_users"}
        ]
        unique_users_result = await AuditLog.aggregate(unique_users_pipeline).to_list(1)
        unique_users = unique_users_result[0]["unique_users"] if unique_users_result else 0
        
        unique_sessions_pipeline = [
            {"$match": {
                "event_timestamp": {"$gte": since_date},
                "session_id": {"$ne": None}
            }},
            {"$group": {"_id": "$session_id"}},
            {"$count": "unique_sessions"}
        ]
        unique_sessions_result = await AuditLog.aggregate(unique_sessions_pipeline).to_list(1)
        unique_sessions = unique_sessions_result[0]["unique_sessions"] if unique_sessions_result else 0
        
        # Most active endpoints
        endpoints_pipeline = [
            {"$match": {
                "event_timestamp": {"$gte": since_date},
                "endpoint": {"$ne": None}
            }},
            {"$group": {"_id": "$endpoint", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_endpoints = await AuditLog.aggregate(endpoints_pipeline).to_list()
        
        return {
            "period_days": days,
            "total_events": total_events,
            "error_count": error_count,
            "error_rate": round((error_count / total_events * 100), 2) if total_events > 0 else 0,
            "unique_users": unique_users,
            "unique_sessions": unique_sessions,
            "event_type_distribution": {item["_id"]: item["count"] for item in event_types},
            "status_code_distribution": {item["_id"]: item["count"] for item in status_codes},
            "performance_statistics": {
                "average_response_time_ms": round(performance.get("avg_response_time") or 0, 2),
                "minimum_response_time_ms": performance.get("min_response_time") or 0,
                "maximum_response_time_ms": performance.get("max_response_time") or 0
            },
            "top_endpoints": [{"endpoint": item["_id"], "count": item["count"]} for item in top_endpoints]
        }
    
    async def cleanup_old_logs(self, retention_days: int = 90) -> int:
        """Clean up old audit logs beyond retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        query = {"event_timestamp": {"$lt": cutoff_date}}
        
        # Count before deletion
        query_to_count = AuditLog.find(query)
        count_to_delete = await query_to_count.count()
        
        # Delete old logs
        await AuditLog.find(query).delete()
        
        return count_to_delete

# Synchronous wrapper for backward compatibility
class SyncAuditLogRepository(SyncRepository[AuditLog]):
    """Synchronous AuditLog repository for backward compatibility"""
    
    def __init__(self):
        super().__init__(AuditLog)
        self.async_repo = AuditLogRepository()
    
    def log_event(self, db, event_type: str, event_action: str, **kwargs) -> AuditLog:
        """Synchronous log_event"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.async_repo.log_event(event_type, event_action, **kwargs))

# Global repository instances
audit_log_repository = SyncAuditLogRepository()  # For backward compatibility
async_audit_log_repository = AuditLogRepository()  # For new async code