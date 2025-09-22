# backend/models/audit_log.py

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field
from bson import ObjectId
from .base import BaseModel

class AuditLog(BaseModel):
    """Audit Log model for tracking all system activities in MongoDB"""
    
    # Event information
    event_type: str = Field(..., index=True)  # resume_upload, job_parse, match_create, etc.
    event_action: str = Field(..., index=True)  # CREATE, UPDATE, DELETE, VIEW
    resource_type: Optional[str] = Field(default=None, index=True)  # resume, job_description, match_result
    resource_id: Optional[ObjectId] = None  # ID of the affected resource
    
    # User and session information
    user_id: Optional[str] = Field(default=None, index=True)  # For future authentication
    session_id: Optional[str] = Field(default=None, index=True)  # Session tracking
    ip_address: Optional[str] = None  # IPv4/IPv6 address
    user_agent: Optional[str] = None  # Browser/client information
    
    # Request details
    endpoint: Optional[str] = Field(default=None, index=True)  # API endpoint called
    http_method: Optional[str] = None  # GET, POST, PUT, DELETE
    request_params: Optional[Dict[str, Any]] = Field(default={})  # Request parameters
    request_body_hash: Optional[str] = None  # SHA256 hash of request body
    
    # Response information
    response_status: Optional[int] = Field(default=None, index=True)  # HTTP status code
    response_time_ms: Optional[int] = None  # Response time in milliseconds
    error_message: Optional[str] = None  # Error details if any
    
    # Processing details
    processing_details: Optional[Dict[str, Any]] = Field(default={})  # Additional processing information
    file_details: Optional[Dict[str, Any]] = Field(default={})  # File information for uploads
    
    # Business context
    business_event: Optional[str] = None  # High-level business description
    correlation_id: Optional[str] = Field(default=None, index=True)  # For tracking related events
    
    # Data changes (for UPDATE/DELETE operations)
    old_values: Optional[Dict[str, Any]] = Field(default={})  # Previous values
    new_values: Optional[Dict[str, Any]] = Field(default={})  # New values
    changed_fields: Optional[List[str]] = Field(default=[])  # List of changed field names
    
    # System information
    server_instance: Optional[str] = None  # Server/container ID
    api_version: Optional[str] = None  # API version used
    client_version: Optional[str] = None  # Client app version
    
    # Compliance and security
    data_classification: Optional[str] = None  # public, internal, confidential
    retention_policy: Optional[str] = None  # Data retention requirements
    compliance_flags: Optional[Dict[str, bool]] = Field(default={})  # GDPR, CCPA, etc. compliance markers
    
    # Use a more precise timestamp
    event_timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    class Settings:
        name = "audit_logs"  # MongoDB collection name
        indexes = [
            "event_type",
            "event_action", 
            "resource_type",
            "user_id",
            "session_id",
            "endpoint",
            "response_status",
            "correlation_id",
            "event_timestamp",
            [("event_type", 1), ("event_timestamp", -1)],  # Compound index for queries
            [("resource_type", 1), ("resource_id", 1)]  # Compound index for resource tracking
        ]