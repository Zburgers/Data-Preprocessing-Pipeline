from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.schemas.task import MLTaskResponse, MLTaskList
from src.services.database import get_db
from src.services.task_service import MLTaskService
from src.utils.logging import logger

router = APIRouter()

@router.get("/", response_model=MLTaskList)
async def list_tasks(
    modality: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all available ML tasks with optional filtering by modality.
    """
    try:
        task_service = MLTaskService(db)
        tasks = await task_service.get_tasks(modality=modality)
        return {"tasks": tasks, "total": len(tasks)}
    except Exception as e:
        logger.error(f"Error listing ML tasks: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{task_id}", response_model=MLTaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific ML task by ID.
    """
    try:
        task_service = MLTaskService(db)
        task = await task_service.get_task(task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ML task with ID {task_id} not found"
            )
            
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving ML task {task_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/detect/{dataset_id}", response_model=List[MLTaskResponse])
async def detect_tasks(
    dataset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Detect suitable ML tasks for a given dataset.
    """
    try:
        task_service = MLTaskService(db)
        suggested_tasks = await task_service.detect_tasks(dataset_id)
        return suggested_tasks
    except Exception as e:
        logger.error(f"Error detecting ML tasks for dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 