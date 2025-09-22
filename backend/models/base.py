# backend/models/base.py

from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field
from bson import ObjectId

class BaseModel(Document):
    """Base model with common fields for MongoDB"""
    
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    
    class Settings:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True  # Allow ObjectId and other MongoDB types
    
    class Config:
        arbitrary_types_allowed = True  # For Pydantic v1 compatibility
        json_encoders = {
            ObjectId: str,  # Convert ObjectId to string for JSON serialization
            datetime: lambda v: v.isoformat()
        }
    
    def save(self, *args, **kwargs):
        """Override save to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
    
    async def save_async(self, *args, **kwargs):
        """Override async save to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return await super().save(*args, **kwargs)