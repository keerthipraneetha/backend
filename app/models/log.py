from pydantic import BaseModel, Field, ConfigDict
from pydantic.json_schema import JsonSchemaValue
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        from pydantic_core import core_schema
        return core_schema.with_info_wrap_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v, handler, info):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: JsonSchemaValue, handler) -> JsonSchemaValue:
        field_schema.update(type="string")
        return field_schema

class LogAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"

class LogBase(BaseModel):
    action: LogAction = Field(..., description="Action performed")
    entityType: str = Field(..., description="Type of entity affected", max_length=50)
    entityId: str = Field(..., description="ID of the affected entity")
    userId: str = Field(..., description="User ID who performed the action")
    userName: str = Field(..., description="User name who performed the action", max_length=100)
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the action occurred")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details about the action")
    ipAddress: Optional[str] = Field(None, description="IP address of the user", max_length=45)

class LogCreate(LogBase):
    pass

class LogResponse(LogBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class LogInDB(LogResponse):
    pass