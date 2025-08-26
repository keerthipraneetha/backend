from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserInDB
from app.services.vehicle_service import VehicleService
from app.services.log_service import LogService
from app.routers.auth import get_current_user_dependency

router = APIRouter()

@router.get("/", response_model=dict)
async def get_dashboard_data(
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Get dashboard statistics and data"""
    vehicle_service = VehicleService()
    log_service = LogService()
    
    try:
        # Get vehicle statistics
        total_vehicles = await vehicle_service.get_total_vehicles()
        vehicles_by_status = await vehicle_service.get_vehicles_by_status()
        vehicles_by_type = await vehicle_service.get_vehicles_by_type()
        
        # Get recent logs
        recent_logs = await log_service.get_recent_logs(limit=10)
        
        # Prepare status counts
        on_duty_count = vehicles_by_status.get("ON_DUTY", 0)
        off_duty_count = vehicles_by_status.get("OFF_DUTY", 0)
        maintenance_count = vehicles_by_status.get("MAINTENANCE", 0)
        
        dashboard_data = {
            "totalVehicles": total_vehicles,
            "onDutyVehicles": on_duty_count,
            "offDutyVehicles": off_duty_count,
            "maintenanceVehicles": maintenance_count,
            "vehiclesByStatus": vehicles_by_status,
            "vehiclesByType": vehicles_by_type,
            "recentLogs": recent_logs
        }
        
        return {
            "success": True,
            "message": "Dashboard data retrieved successfully",
            "data": dashboard_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )