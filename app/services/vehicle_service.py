from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_collection
from app.models.vehicle import VehicleCreate, VehicleUpdate, VehicleInDB

class VehicleService:
    def __init__(self):
        self.collection_name = "vehicles"

    async def get_vehicles_paginated(
        self, 
        page: int = 1, 
        limit: int = 10, 
        filters: Dict[str, Any] = None,
        sorting: Dict[str, int] = None
    ) -> Tuple[List[VehicleInDB], int]:
        """Get vehicles with pagination and filtering"""
        collection = await get_collection(self.collection_name)
        
        # Build query
        query = {"isDeleted": False}
        
        if filters:
            if "search" in filters:
                search_term = filters["search"]
                query["$or"] = [
                    {"VehRegNo": {"$regex": search_term, "$options": "i"}},
                    {"MakeType": {"$regex": search_term, "$options": "i"}},
                    {"Model": {"$regex": search_term, "$options": "i"}},
                    {"PresentUnitName": {"$regex": search_term, "$options": "i"}}
                ]
            
            for key, value in filters.items():
                if key != "search" and value:
                    query[key] = value
        
        # Count total documents
        total_count = await collection.count_documents(query)
        
        # Calculate skip value
        skip = (page - 1) * limit
        
        # Build sort criteria
        sort_criteria = sorting if sorting else {"CreatedAt": -1}
        
        # Execute query
        cursor = collection.find(query).sort(list(sort_criteria.items())).skip(skip).limit(limit)
        vehicles = []
        
        async for document in cursor:
            vehicle = VehicleInDB(**document)
            vehicles.append(vehicle)
        
        return vehicles, total_count

    async def get_vehicle_by_id(self, vehicle_id: str) -> Optional[VehicleInDB]:
        """Get a vehicle by ID"""
        collection = await get_collection(self.collection_name)
        
        try:
            document = await collection.find_one({
                "_id": ObjectId(vehicle_id),
                "isDeleted": False
            })
            
            if document:
                return VehicleInDB(**document)
            return None
        except Exception:
            return None

    async def get_vehicle_by_reg_no(self, reg_no: str) -> Optional[VehicleInDB]:
        """Get a vehicle by registration number"""
        collection = await get_collection(self.collection_name)
        
        document = await collection.find_one({
            "VehRegNo": reg_no,
            "isDeleted": False
        })
        
        if document:
            return VehicleInDB(**document)
        return None

    async def create_vehicle(self, vehicle_data: VehicleCreate, created_by: str) -> VehicleInDB:
        """Create a new vehicle"""
        collection = await get_collection(self.collection_name)
        
        now = datetime.utcnow()
        
        vehicle_dict = vehicle_data.dict()
        vehicle_dict.update({
            "CreatedBy": created_by,
            "CreatedAt": now,
            "UpdatedBy": created_by,
            "UpdatedAt": now,
            "IsActive": True,
            "isDeleted": False
        })
        
        result = await collection.insert_one(vehicle_dict)
        vehicle_dict["_id"] = result.inserted_id
        
        return VehicleInDB(**vehicle_dict)

    async def update_vehicle(
        self, 
        vehicle_id: str, 
        vehicle_data: VehicleUpdate, 
        updated_by: str
    ) -> Optional[VehicleInDB]:
        """Update a vehicle"""
        collection = await get_collection(self.collection_name)
        
        update_dict = vehicle_data.dict(exclude_unset=True)
        if not update_dict:
            return await self.get_vehicle_by_id(vehicle_id)
        
        update_dict.update({
            "UpdatedBy": updated_by,
            "UpdatedAt": datetime.utcnow()
        })
        
        await collection.update_one(
            {"_id": ObjectId(vehicle_id), "isDeleted": False},
            {"$set": update_dict}
        )
        
        return await self.get_vehicle_by_id(vehicle_id)

    async def delete_vehicle(self, vehicle_id: str, deleted_by: str) -> bool:
        """Soft delete a vehicle"""
        collection = await get_collection(self.collection_name)
        
        result = await collection.update_one(
            {"_id": ObjectId(vehicle_id), "isDeleted": False},
            {
                "$set": {
                    "isDeleted": True,
                    "UpdatedBy": deleted_by,
                    "UpdatedAt": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0

    async def get_total_vehicles(self) -> int:
        """Get total count of active vehicles"""
        collection = await get_collection(self.collection_name)
        return await collection.count_documents({"isDeleted": False})

    async def get_vehicles_by_status(self) -> Dict[str, int]:
        """Get vehicle count grouped by status"""
        collection = await get_collection(self.collection_name)
        
        pipeline = [
            {"$match": {"isDeleted": False}},
            {"$group": {"_id": "$Status", "count": {"$sum": 1}}}
        ]
        
        cursor = collection.aggregate(pipeline)
        status_counts = {}
        
        async for doc in cursor:
            status_counts[doc["_id"]] = doc["count"]
        
        return status_counts

    async def get_vehicles_by_type(self) -> Dict[str, int]:
        """Get vehicle count grouped by type"""
        collection = await get_collection(self.collection_name)
        
        pipeline = [
            {"$match": {"isDeleted": False}},
            {"$group": {"_id": "$VehicleType", "count": {"$sum": 1}}}
        ]
        
        cursor = collection.aggregate(pipeline)
        type_counts = {}
        
        async for doc in cursor:
            type_counts[doc["_id"]] = doc["count"]
        
        return type_counts