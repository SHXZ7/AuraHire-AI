# backend/crud/base.py

from typing import Type, TypeVar, Generic, List, Optional, Dict, Any
from bson import ObjectId
from beanie import Document

ModelType = TypeVar("ModelType", bound=Document)

class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations for MongoDB with Beanie"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    # Create operations
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        await db_obj.save()
        return db_obj
    
    # Read operations
    async def get(self, id: str) -> Optional[ModelType]:
        """Get a record by ID"""
        try:
            return await self.model.get(ObjectId(id))
        except:
            return None
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        sort_field: str = "created_at",
        sort_direction: int = -1  # -1 for descending, 1 for ascending
    ) -> List[ModelType]:
        """Get multiple records with pagination"""
        sort_criteria = [(sort_field, sort_direction)]
        return await self.model.find_all().sort(sort_criteria).skip(skip).limit(limit).to_list()
    
    async def count(self) -> int:
        """Count total records"""
        return await self.model.count()
    
    # Update operations
    async def update(self, id: str, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record by ID"""
        db_obj = await self.get(id)
        if db_obj:
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            await db_obj.save()
        return db_obj
    
    # Delete operations
    async def delete(self, id: str) -> bool:
        """Delete a record by ID"""
        db_obj = await self.get(id)
        if db_obj:
            await db_obj.delete()
            return True
        return False
    
    # Search operations
    async def find_by_field(
        self, 
        field: str, 
        value: Any, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """Find records by a specific field value"""
        query = {field: value}
        return await self.model.find(query).skip(skip).limit(limit).to_list()
    
    async def search(
        self, 
        filters: Dict[str, Any], 
        skip: int = 0, 
        limit: int = 100,
        sort_field: str = "created_at",
        sort_direction: int = -1
    ) -> List[ModelType]:
        """Search records with multiple filters"""
        sort_criteria = [(sort_field, sort_direction)]
        return await self.model.find(filters).sort(sort_criteria).skip(skip).limit(limit).to_list()

# Synchronous compatibility functions for non-async contexts
class SyncRepository(Generic[ModelType]):
    """Synchronous wrapper for compatibility with existing code"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.async_repo = BaseRepository(model)
    
    def create(self, db, obj_in: Dict[str, Any]) -> ModelType:
        """Synchronous create - use with caution, prefer async"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.async_repo.create(obj_in))
    
    def get_multi(self, db, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Synchronous get_multi - use with caution, prefer async"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.async_repo.get_multi(skip, limit))
    
    def count(self, db) -> int:
        """Synchronous count - use with caution, prefer async"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.async_repo.count())
    
    def get_multi(
        self, 
        db, 
        skip: int = 0, 
        limit: int = 100,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> List[ModelType]:
        """Get multiple records with pagination"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.async_repo.get_multi(skip=skip, limit=limit))
    
    def update(self, db, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Update a record"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Convert to string ID if it's an ObjectId
        obj_id = str(db_obj.id) if hasattr(db_obj, 'id') else None
        return loop.run_until_complete(self.async_repo.update(obj_id, obj_in))
    
    def delete(self, db, id: str) -> Optional[ModelType]:
        """Delete a record by ID"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.async_repo.delete(id))
    
    def count(self, db, **filters) -> int:
        """Count records with optional filters"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.async_repo.count())