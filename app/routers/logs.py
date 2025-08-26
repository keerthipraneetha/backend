from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from datetime import datetime
from app.models.user import UserInDB
from app.services.log_service import LogService
from app.routers.auth import get_current_user_dependency

router = APIRouter()

@router.get("/", response_model=dict)
async def get_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_user_dependency)
):
    """Get logs with pagination and filtering"""
    log_service = LogService()
    
    try:
        filters = {}
        
        if action:
            filters["action"] = action
        if entity_type:
            filters["entityType"] = entity_type
        if user_id:
            filters["userId"] = user_id
        
        # Date filtering
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            if end_date:
                date_filter["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            if date_filter:
                filters["timestamp"] = date_filter
        
        logs, total_count = await log_service.get_logs_paginated(
            page=page,
            limit=limit,
            filters=filters
        )
        
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "success": True,
            "message": "Logs retrieved successfully",
            "data": {
                "data": logs,
                "total": total_count,
                "page": page,
                "limit": limit,
                "totalPages": total_pages
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )