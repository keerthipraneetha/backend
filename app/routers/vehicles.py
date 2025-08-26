from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from app.models.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from app.models.user import UserInDB
from app.services.vehicle_service import VehicleService
from app.services.log_service import LogService
from app.routers.auth import get_current_user_dependency

router = APIRouter()

@router.get("/", response_model=dict)
async def get_vehicles(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    vehicle_type: Optional[str] = None,
    fuel_type: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$"),
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Get vehicles with pagination and filtering"""
    vehicle_service = VehicleService()
    
    try:
        filters = {}
        if search:
            filters["search"] = search
        if status:
            filters["Status"] = status
        if vehicle_type:
            filters["VehicleType"] = vehicle_type
        if fuel_type:
            filters["FuelType"] = fuel_type
        
        sorting = {}
        if sort_by:
            sorting[sort_by] = 1 if sort_order == "asc" else -1
        
        vehicles, total_count = await vehicle_service.get_vehicles_paginated(
            page=page,
            limit=limit,
            filters=filters,
            sorting=sorting
        )
        
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "success": True,
            "message": "Vehicles retrieved successfully",
            "data": {
                "data": vehicles,
                "total": total_count,
                "page": page,
                "limit": limit,
                "totalPages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{vehicle_id}", response_model=dict)
async def get_vehicle(
    vehicle_id: str,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Get a specific vehicle by ID"""
    vehicle_service = VehicleService()
    log_service = LogService()
    
    try:
        vehicle = await vehicle_service.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Log the view action
        await log_service.create_log(
            action="VIEW",
            entity_type="vehicle",
            entity_id=vehicle_id,
            user_id=str(current_user.id),
            user_name=current_user.fullName,
            details={"VehRegNo": vehicle.VehRegNo}
        )
        
        return {
            "success": True,
            "message": "Vehicle retrieved successfully",
            "data": vehicle
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/", response_model=dict)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Create a new vehicle"""
    vehicle_service = VehicleService()
    log_service = LogService()
    
    try:
        # Check if vehicle registration number already exists
        existing_vehicle = await vehicle_service.get_vehicle_by_reg_no(vehicle_data.VehRegNo)
        if existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle with this registration number already exists"
            )
        
        # Create vehicle
        vehicle = await vehicle_service.create_vehicle(
            vehicle_data=vehicle_data,
            created_by=str(current_user.id)
        )
        
        # Log the creation
        await log_service.create_log(
            action="CREATE",
            entity_type="vehicle",
            entity_id=str(vehicle.id),
            user_id=str(current_user.id),
            user_name=current_user.fullName,
            details={
                "VehRegNo": vehicle.VehRegNo,
                "MakeType": vehicle.MakeType,
                "Model": vehicle.Model,
                "Status": vehicle.Status
            }
        )
        
        return {
            "success": True,
            "message": "Vehicle created successfully",
            "data": vehicle
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{vehicle_id}", response_model=dict)
async def update_vehicle(
    vehicle_id: str,
    vehicle_data: VehicleUpdate,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Update a vehicle"""
    vehicle_service = VehicleService()
    log_service = LogService()
    
    try:
        # Check if vehicle exists
        existing_vehicle = await vehicle_service.get_vehicle_by_id(vehicle_id)
        if not existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Check if updating registration number and it's already taken
        if vehicle_data.VehRegNo and vehicle_data.VehRegNo != existing_vehicle.VehRegNo:
            reg_check = await vehicle_service.get_vehicle_by_reg_no(vehicle_data.VehRegNo)
            if reg_check:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vehicle with this registration number already exists"
                )
        
        # Update vehicle
        updated_vehicle = await vehicle_service.update_vehicle(
            vehicle_id=vehicle_id,
            vehicle_data=vehicle_data,
            updated_by=str(current_user.id)
        )
        
        # Prepare changes for logging
        changes = {}
        for field, value in vehicle_data.dict(exclude_unset=True).items():
            if value is not None:
                changes[field] = value
        
        # Log the update
        await log_service.create_log(
            action="UPDATE",
            entity_type="vehicle",
            entity_id=vehicle_id,
            user_id=str(current_user.id),
            user_name=current_user.fullName,
            details={
                "VehRegNo": updated_vehicle.VehRegNo,
                "changes": changes
            }
        )
        
        return {
            "success": True,
            "message": "Vehicle updated successfully",
            "data": updated_vehicle
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{vehicle_id}", response_model=dict)
async def delete_vehicle(
    vehicle_id: str,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Delete a vehicle (soft delete)"""
    vehicle_service = VehicleService()
    log_service = LogService()
    
    try:
        # Check if vehicle exists
        vehicle = await vehicle_service.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Soft delete vehicle
        await vehicle_service.delete_vehicle(
            vehicle_id=vehicle_id,
            deleted_by=str(current_user.id)
        )
        
        # Log the deletion
        await log_service.create_log(
            action="DELETE",
            entity_type="vehicle",
            entity_id=vehicle_id,
            user_id=str(current_user.id),
            user_name=current_user.fullName,
            details={
                "VehRegNo": vehicle.VehRegNo,
                "MakeType": vehicle.MakeType,
                "Model": vehicle.Model
            }
        )
        
        return {
            "success": True,
            "message": "Vehicle deleted successfully",
            "data": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/bulk-delete", response_model=dict)
async def bulk_delete_vehicles(
    vehicle_ids: List[str],
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Delete multiple vehicles (soft delete)"""
    vehicle_service = VehicleService()
    log_service = LogService()
    
    try:
        deleted_count = 0
        deleted_vehicles = []
        
        for vehicle_id in vehicle_ids:
            # Check if vehicle exists
            vehicle = await vehicle_service.get_vehicle_by_id(vehicle_id)
            if vehicle:
                # Soft delete vehicle
                await vehicle_service.delete_vehicle(
                    vehicle_id=vehicle_id,
                    deleted_by=str(current_user.id)
                )
                deleted_count += 1
                deleted_vehicles.append(vehicle.VehRegNo)
                
                # Log the deletion
                await log_service.create_log(
                    action="DELETE",
                    entity_type="vehicle",
                    entity_id=vehicle_id,
                    user_id=str(current_user.id),
                    user_name=current_user.fullName,
                    details={
                        "VehRegNo": vehicle.VehRegNo,
                        "bulk_delete": True
                    }
                )
        
        return {
            "success": True,
            "message": f"{deleted_count} vehicles deleted successfully",
            "data": {
                "deleted_count": deleted_count,
                "deleted_vehicles": deleted_vehicles
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )