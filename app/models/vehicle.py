from pydantic import BaseModel, Field, ConfigDict
from pydantic.json_schema import JsonSchemaValue
from typing import Optional, Any
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

class FuelType(str, Enum):
    PETROL = "PETROL"
    DIESEL = "DIESEL"
    CNG = "CNG"
    LPG = "LPG"
    ELECTRIC = "ELECTRIC"
    HYBRID = "HYBRID"

class Provision(str, Enum):
    OWNED = "OWNED"
    LEASED = "LEASED"
    HIRED = "HIRED"
    DONATED = "DONATED"

class VehicleCondition(str, Enum):
    NEW = "NEW"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    UNSERVICEABLE = "UNSERVICEABLE"

class VehicleStatus(str, Enum):
    ON_DUTY = "ON_DUTY"
    OFF_DUTY = "OFF_DUTY"
    MAINTENANCE = "MAINTENANCE"

class VehicleType(str, Enum):
    TWO_WHEELER = "TWO_WHEELER"
    THREE_WHEELER = "THREE_WHEELER"
    CAR = "CAR"
    SUV = "SUV"
    VAN = "VAN"
    BUS = "BUS"
    TRUCK = "TRUCK"
    TRACTOR = "TRACTOR"
    SPECIAL_PURPOSE = "SPECIAL_PURPOSE"

class VehicleBase(BaseModel):
    VehRegNo: str = Field(..., description="Vehicle Registration Number", max_length=20)
    CustomerID: str = Field(..., description="Customer ID")
    MakeType: str = Field(..., description="Vehicle Make Type", max_length=50)
    Model: str = Field(..., description="Vehicle Model", max_length=50)
    KMPL: float = Field(..., description="Kilometers per Liter", gt=0)
    VehicleGroup: str = Field(..., description="Vehicle Group", max_length=50)
    Category: str = Field(..., description="Vehicle Category", max_length=50)
    PurchaseDate: datetime = Field(..., description="Purchase Date")
    VehicleCost: float = Field(..., description="Vehicle Cost", gt=0)
    PurchasedFrom: str = Field(..., description="Purchased From", max_length=100)
    RegistrationDate: datetime = Field(..., description="Registration Date")
    fuel_type: FuelType = Field(..., description="Fuel Type")
    TankCapacity: float = Field(..., description="Tank Capacity in Liters", gt=0)
    SeatingCapacity: int = Field(..., description="Seating Capacity", gt=0)
    provision: Provision = Field(..., description="Vehicle Provision")
    unitId: str = Field(..., description="Unit ID")
    PresentUnitName: str = Field(..., description="Present Unit Name", max_length=100)
    PreviousUnitName: Optional[str] = Field(None, description="Previous Unit Name", max_length=100)
    EngineNumber: str = Field(..., description="Engine Number", max_length=50)
    ChassisNumber: str = Field(..., description="Chassis Number", max_length=50)
    GoDate: datetime = Field(..., description="GO Date")
    GoNumber: str = Field(..., description="GO Number", max_length=50)
    vehicle_condition: VehicleCondition = Field(..., description="Vehicle Condition")
    Remarks: Optional[str] = Field(None, description="Remarks", max_length=500)
    status: VehicleStatus = Field(..., description="Vehicle Status")
    vehicle_type: VehicleType = Field(..., description="Vehicle Type")

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    VehRegNo: Optional[str] = Field(None, max_length=20)
    CustomerID: Optional[str] = None
    MakeType: Optional[str] = Field(None, max_length=50)
    Model: Optional[str] = Field(None, max_length=50)
    KMPL: Optional[float] = Field(None, gt=0)
    VehicleGroup: Optional[str] = Field(None, max_length=50)
    Category: Optional[str] = Field(None, max_length=50)
    PurchaseDate: Optional[datetime] = None
    VehicleCost: Optional[float] = Field(None, gt=0)
    PurchasedFrom: Optional[str] = Field(None, max_length=100)
    RegistrationDate: Optional[datetime] = None
    fuel_type: Optional[FuelType] = None
    TankCapacity: Optional[float] = Field(None, gt=0)
    SeatingCapacity: Optional[int] = Field(None, gt=0)
    provision: Optional[Provision] = None
    unitId: Optional[str] = None
    PresentUnitName: Optional[str] = Field(None, max_length=100)
    PreviousUnitName: Optional[str] = Field(None, max_length=100)
    EngineNumber: Optional[str] = Field(None, max_length=50)
    ChassisNumber: Optional[str] = Field(None, max_length=50)
    GoDate: Optional[datetime] = None
    GoNumber: Optional[str] = Field(None, max_length=50)
    vehicle_condition: Optional[VehicleCondition] = None
    Remarks: Optional[str] = Field(None, max_length=500)
    status: Optional[VehicleStatus] = None
    vehicle_type: Optional[VehicleType] = None

class VehicleResponse(VehicleBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    CreatedBy: str = Field(..., description="Created By User ID")
    CreatedAt: datetime = Field(..., description="Creation Timestamp")
    UpdatedBy: str = Field(..., description="Updated By User ID")
    UpdatedAt: datetime = Field(..., description="Update Timestamp")
    IsActive: bool = Field(default=True, description="Is Active")
    isDeleted: bool = Field(default=False, description="Is Deleted")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class VehicleInDB(VehicleResponse):
    pass