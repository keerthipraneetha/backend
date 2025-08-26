from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.core.database import get_collection
from app.core.security import get_password_hash, verify_password
from app.models.user import UserCreate, UserUpdate, UserInDB

class UserService:
    def __init__(self):
        self.collection_name = "users"

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get a user by ID"""
        collection = await get_collection(self.collection_name)
        
        try:
            document = await collection.find_one({
                "_id": ObjectId(user_id),
                "IsActive": True
            })
            
            if document:
                return UserInDB(**document)
            return None
        except Exception:
            return None

    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Get a user by username"""
        collection = await get_collection(self.collection_name)
        
        document = await collection.find_one({
            "username": username,
            "IsActive": True
        })
        
        if document:
            return UserInDB(**document)
        return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get a user by email"""
        collection = await get_collection(self.collection_name)
        
        document = await collection.find_one({
            "email": email,
            "IsActive": True
        })
        
        if document:
            return UserInDB(**document)
        return None

    async def create_user(self, user_data: UserCreate) -> UserInDB:
        """Create a new user"""
        collection = await get_collection(self.collection_name)
        
        now = datetime.utcnow()
        
        user_dict = user_data.dict()
        user_dict.update({
            "password": get_password_hash(user_data.password),
            "IsActive": True,
            "CreatedAt": now,
            "UpdatedAt": now
        })
        
        result = await collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        return UserInDB(**user_dict)

    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """Authenticate a user with username and password"""
        user = await self.get_user_by_username(username)
        
        if not user:
            return None
        
        if not verify_password(password, user.password):
            return None
        
        return user

    async def update_user(
        self, 
        user_id: str, 
        user_data: UserUpdate
    ) -> Optional[UserInDB]:
        """Update a user"""
        collection = await get_collection(self.collection_name)
        
        update_dict = user_data.dict(exclude_unset=True)
        if not update_dict:
            return await self.get_user_by_id(user_id)
        
        update_dict.update({
            "UpdatedAt": datetime.utcnow()
        })
        
        await collection.update_one(
            {"_id": ObjectId(user_id), "IsActive": True},
            {"$set": update_dict}
        )
        
        return await self.get_user_by_id(user_id)

    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user (soft delete)"""
        collection = await get_collection(self.collection_name)
        
        result = await collection.update_one(
            {"_id": ObjectId(user_id), "IsActive": True},
            {
                "$set": {
                    "IsActive": False,
                    "UpdatedAt": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0