# backend/crud/audit_log.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
from .base import BaseRepository
from ..models.audit_log import AuditLog

class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for Audit Log operations"""
    
    def __init__(self):
        super().__init__(AuditLog)
    
    def log_event(
        self,
        db: Session,
        event_type: str,
        event_action: str,
        resource_type: str = None,
        resource_id: int = None,
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
            if hasattr(AuditLog, key):
                log_data[key] = value
        
        return self.create(db, log_data)
    
    def get_by_event_type(self, db: Session, event_type: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by event type"""
        return (
            db.query(AuditLog)
            .filter(AuditLog.event_type == event_type)
            .order_by(desc(AuditLog.event_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_resource(self, db: Session, resource_type: str, resource_id: int, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific resource"""
        return (
            db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.resource_type == resource_type,
                    AuditLog.resource_id == resource_id
                )
            )
            .order_by(desc(AuditLog.event_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific user"""
        return (
            db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(desc(AuditLog.event_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_session(self, db: Session, session_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific session"""
        return (
            db.query(AuditLog)
            .filter(AuditLog.session_id == session_id)
            .order_by(desc(AuditLog.event_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_correlation(self, db: Session, correlation_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get related audit logs by correlation ID"""
        return (
            db.query(AuditLog)
            .filter(AuditLog.correlation_id == correlation_id)
            .order_by(AuditLog.event_timestamp)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_date_range(
        self, 
        db: Session, 
        start_date: datetime, 
        end_date: datetime, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs within date range"""
        return (
            db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.event_timestamp >= start_date,
                    AuditLog.event_timestamp <= end_date
                )
            )
            .order_by(desc(AuditLog.event_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_errors(self, db: Session, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs with errors"""
        return (
            db.query(AuditLog)
            .filter(AuditLog.error_message.isnot(None))
            .order_by(desc(AuditLog.event_timestamp))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_slow_requests(self, db: Session, min_time_ms: int = 1000, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for slow requests"""
        return (
            db.query(AuditLog)
            .filter(AuditLog.response_time_ms >= min_time_ms)
            .order_by(desc(AuditLog.response_time_ms))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_statistics(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """Get audit log statistics for the last N days"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Total events
        total_events = db.query(AuditLog).filter(AuditLog.event_timestamp >= since_date).count()
        
        # Event type distribution
        event_types = (
            db.query(AuditLog.event_type, func.count(AuditLog.id).label('count'))
            .filter(AuditLog.event_timestamp >= since_date)
            .group_by(AuditLog.event_type)
            .order_by(func.count(AuditLog.id).desc())
            .all()
        )
        
        # Response status distribution
        status_codes = (
            db.query(AuditLog.response_status, func.count(AuditLog.id).label('count'))
            .filter(
                and_(
                    AuditLog.event_timestamp >= since_date,
                    AuditLog.response_status.isnot(None)
                )
            )
            .group_by(AuditLog.response_status)
            .order_by(func.count(AuditLog.id).desc())
            .all()
        )
        
        # Error count
        error_count = (
            db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.event_timestamp >= since_date,
                    AuditLog.error_message.isnot(None)
                )
            )
            .count()
        )
        
        # Performance statistics
        performance_stats = db.query(
            func.avg(AuditLog.response_time_ms).label('avg_response_time'),
            func.min(AuditLog.response_time_ms).label('min_response_time'),
            func.max(AuditLog.response_time_ms).label('max_response_time')
        ).filter(
            and_(
                AuditLog.event_timestamp >= since_date,
                AuditLog.response_time_ms.isnot(None)
            )
        ).first()
        
        # Active users/sessions
        unique_users = (
            db.query(func.count(func.distinct(AuditLog.user_id)))
            .filter(
                and_(
                    AuditLog.event_timestamp >= since_date,
                    AuditLog.user_id.isnot(None)
                )
            )
            .scalar()
        )
        
        unique_sessions = (
            db.query(func.count(func.distinct(AuditLog.session_id)))
            .filter(
                and_(
                    AuditLog.event_timestamp >= since_date,
                    AuditLog.session_id.isnot(None)
                )
            )
            .scalar()
        )
        
        # Most active endpoints
        top_endpoints = (
            db.query(AuditLog.endpoint, func.count(AuditLog.id).label('count'))
            .filter(
                and_(
                    AuditLog.event_timestamp >= since_date,
                    AuditLog.endpoint.isnot(None)
                )
            )
            .group_by(AuditLog.endpoint)
            .order_by(func.count(AuditLog.id).desc())
            .limit(10)
            .all()
        )
        
        return {
            "period_days": days,
            "total_events": total_events,
            "error_count": error_count,
            "error_rate": round((error_count / total_events * 100), 2) if total_events > 0 else 0,
            "unique_users": unique_users,
            "unique_sessions": unique_sessions,
            "event_type_distribution": {event_type: count for event_type, count in event_types},
            "status_code_distribution": {status: count for status, count in status_codes},
            "performance_statistics": {
                "average_response_time_ms": round(performance_stats.avg_response_time, 2) if performance_stats.avg_response_time else 0,
                "minimum_response_time_ms": performance_stats.min_response_time if performance_stats.min_response_time else 0,
                "maximum_response_time_ms": performance_stats.max_response_time if performance_stats.max_response_time else 0
            },
            "top_endpoints": [{"endpoint": endpoint, "count": count} for endpoint, count in top_endpoints]
        }
    
    def cleanup_old_logs(self, db: Session, retention_days: int = 90) -> int:
        """Clean up old audit logs beyond retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        deleted_count = (
            db.query(AuditLog)
            .filter(AuditLog.event_timestamp < cutoff_date)
            .delete()
        )
        db.commit()
        return deleted_count
    
    # Async versions
    async def log_event_async(self, db: AsyncSession, **kwargs) -> AuditLog:
        """Log a new audit event (async)"""
        log_data = {
            "event_timestamp": datetime.utcnow(),
            **kwargs
        }
        return await self.create_async(db, log_data)

# Global repository instance
audit_log_repository = AuditLogRepository()