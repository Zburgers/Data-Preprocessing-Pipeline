from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.schemas.step import PipelineStepResponse, PipelineStepList
from src.services.database import get_db
from src.services.step_service import PipelineStepService
from src.utils.logging import logger

router = APIRouter()

@router.get("/", response_model=PipelineStepList)
async def list_steps(
    modality: Optional[str] = None,
    step_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all available pipeline steps with optional filtering by modality and step type.
    """
    try:
        step_service = PipelineStepService(db)
        steps = await step_service.get_steps(modality=modality, step_type=step_type)
        return {"steps": steps, "total": len(steps)}
    except Exception as e:
        logger.error(f"Error listing pipeline steps: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{step_id}", response_model=PipelineStepResponse)
async def get_step(
    step_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific pipeline step by ID.
    """
    try:
        step_service = PipelineStepService(db)
        step = await step_service.get_step(step_id)
        
        if not step:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline step with ID {step_id} not found"
            )
            
        return step
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving pipeline step {step_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/task/{task_id}", response_model=PipelineStepList)
async def get_steps_by_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all pipeline steps recommended for a specific ML task.
    """
    try:
        step_service = PipelineStepService(db)
        steps = await step_service.get_steps_by_task(task_id)
        return {"steps": steps, "total": len(steps)}
    except Exception as e:
        logger.error(f"Error retrieving pipeline steps for task {task_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/compatible/{step_id}", response_model=PipelineStepList)
async def get_compatible_steps(
    step_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all pipeline steps that are compatible with the given step.
    """
    try:
        step_service = PipelineStepService(db)
        steps = await step_service.get_compatible_steps(step_id)
        return {"steps": steps, "total": len(steps)}
    except Exception as e:
        logger.error(f"Error retrieving compatible steps for step {step_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 