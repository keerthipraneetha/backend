from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from app.core.database import get_collection
from app.models.log import LogCreate, LogInDB, LogAction

class LogService:
    def __init__(self):
        self.collection_name = "logs"

    async def create_log(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: str,
        user_name: str,
        details: Dict[str, Any] = None,
        ip_address: Optional[str] = None
    ) -> LogInDB:
        """Create a new log entry"""
        collection = await get_collection(self.collection_name)
        
        log_data = {
            "action": action,
            "entityType": entity_type,
            "entityId": entity_id,
            "userId": user_id,
            "userName": user_name,
            "timestamp": datetime.utcnow(),
            "details": details or {},
            "ipAddress": ip_address
        }
        
        result = await collection.insert_one(log_data)
        log_data["_id"] = result.inserted_id
        
        return LogInDB(**log_data)

    async def get_logs_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        filters: Dict[str, Any] = None
    ) -> Tuple[List[LogInDB], int]:
        """Get logs with pagination and filtering"""
        collection = await get_collection(self.collection_name)
        
        # Build query
        query = {}
        if filters:
            query.update(filters)
        
        # Count total documents
        total_count = await collection.count_documents(query)
        
        # Calculate skip value
        skip = (page - 1) * limit
        
        # Execute query with sorting by timestamp (newest first)
        cursor = collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        logs = []
        
        async for document in cursor:
            log = LogInDB(**document)
            logs.append(log)
        
        return logs, total_count

    async def get_recent_logs(self, limit: int = 10) -> List[LogInDB]:
        """Get recent log entries"""
        collection = await get_collection(self.collection_name)
        
        cursor = collection.find().sort("timestamp", -1).limit(limit)
        logs = []
        
        async for document in cursor:
            log = LogInDB(**document)
            logs.append(log)
        
        return logs

    async def get_logs_by_user(self, user_id: str, limit: int = 50) -> List[LogInDB]:
        """Get logs for a specific user"""
        collection = await get_collection(self.collection_name)
        
        cursor = collection.find({"userId": user_id}).sort("timestamp", -1).limit(limit)
        logs = []
        
        async for document in cursor:
            log = LogInDB(**document)
            logs.append(log)
        
        return logs

    async def get_logs_by_entity(
        self, 
        entity_type: str, 
        entity_id: str, 
        limit: int = 50
    ) -> List[LogInDB]:
        """Get logs for a specific entity"""
        collection = await get_collection(self.collection_name)
        
        query = {
            "entityType": entity_type,
            "entityId": entity_id
        }
        
        cursor = collection.find(query).sort("timestamp", -1).limit(limit)
        logs = []
        
        async for document in cursor:
            log = LogInDB(**document)
            logs.append(log)
        
        return logs

    async def delete_old_logs(self, days_to_keep: int = 90) -> int:
        """Delete logs older than specified days (for cleanup)"""
        collection = await get_collection(self.collection_name)
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        result = await collection.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        
        return result.deleted_count