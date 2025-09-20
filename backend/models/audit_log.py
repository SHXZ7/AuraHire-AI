# backend/models/audit_log.py

from sqlalchemy import Column, String, Text, JSON, Integer, DateTime
from sqlalchemy.sql import func
from .base import BaseModel

class AuditLog(BaseModel):
    """Audit Log model for tracking all system activities"""
    __tablename__ = "audit_logs"
    
    # Event information
    event_type = Column(String(100), nullable=False)  # resume_upload, job_parse, match_create, etc.
    event_action = Column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, VIEW
    resource_type = Column(String(100))  # resume, job_description, match_result
    resource_id = Column(Integer)  # ID of the affected resource
    
    # User and session information
    user_id = Column(String(255))  # For future authentication
    session_id = Column(String(255))  # Session tracking
    ip_address = Column(String(45))  # IPv4/IPv6 address
    user_agent = Column(Text)  # Browser/client information
    
    # Request details
    endpoint = Column(String(255))  # API endpoint called
    http_method = Column(String(10))  # GET, POST, PUT, DELETE
    request_params = Column(JSON)  # Request parameters
    request_body_hash = Column(String(64))  # SHA256 hash of request body
    
    # Response information
    response_status = Column(Integer)  # HTTP status code
    response_time_ms = Column(Integer)  # Response time in milliseconds
    error_message = Column(Text)  # Error details if any
    
    # Processing details
    processing_details = Column(JSON)  # Additional processing information
    file_details = Column(JSON)  # File information for uploads
    
    # Business context
    business_event = Column(String(255))  # High-level business description
    correlation_id = Column(String(255))  # For tracking related events
    
    # Data changes (for UPDATE/DELETE operations)
    old_values = Column(JSON)  # Previous values
    new_values = Column(JSON)  # New values
    changed_fields = Column(JSON)  # List of changed field names
    
    # System information
    server_instance = Column(String(100))  # Server/container ID
    api_version = Column(String(20))  # API version used
    client_version = Column(String(20))  # Client app version
    
    # Compliance and security
    data_classification = Column(String(50))  # public, internal, confidential
    retention_policy = Column(String(50))  # Data retention requirements
    compliance_flags = Column(JSON)  # GDPR, CCPA, etc. compliance markers
    
    # Override the base created_at to add more precision
    event_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)