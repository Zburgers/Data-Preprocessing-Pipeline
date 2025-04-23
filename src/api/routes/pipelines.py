from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.schemas.pipeline import PipelineCreate, PipelineResponse, PipelineList, PipelineUpdate
from src.services.database import get_db
from src.services.pipeline_service import PipelineService
from src.utils.logging import logger

router = APIRouter()

@router.post("/", response_model=PipelineResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(
    pipeline_data: PipelineCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new preprocessing pipeline.
    """
    try:
        pipeline_service = PipelineService(db)
        new_pipeline = await pipeline_service.create_pipeline(pipeline_data)
        return new_pipeline
    except Exception as e:
        logger.error(f"Error creating pipeline: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=PipelineList)
async def list_pipelines(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    List all available pipelines with pagination.
    """
    try:
        pipeline_service = PipelineService(db)
        pipelines = await pipeline_service.get_pipelines(skip, limit)
        return {"pipelines": pipelines, "total": len(pipelines)}
    except Exception as e:
        logger.error(f"Error listing pipelines: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific pipeline by ID.
    """
    try:
        pipeline_service = PipelineService(db)
        pipeline = await pipeline_service.get_pipeline(pipeline_id)
        
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline with ID {pipeline_id} not found"
            )
            
        return pipeline
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving pipeline {pipeline_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: int,
    pipeline_data: PipelineUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a pipeline by ID.
    """
    try:
        pipeline_service = PipelineService(db)
        updated_pipeline = await pipeline_service.update_pipeline(pipeline_id, pipeline_data)
        
        if not updated_pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline with ID {pipeline_id} not found"
            )
            
        return updated_pipeline
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating pipeline {pipeline_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline(
    pipeline_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a pipeline by ID.
    """
    try:
        pipeline_service = PipelineService(db)
        success = await pipeline_service.delete_pipeline(pipeline_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline with ID {pipeline_id} not found"
            )
            
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting pipeline {pipeline_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{pipeline_id}/execute/{dataset_id}", response_model=dict)
async def execute_pipeline(
    pipeline_id: int,
    dataset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a pipeline on a specific dataset.
    """
    try:
        pipeline_service = PipelineService(db)
        
        # Check if pipeline exists
        pipeline = await pipeline_service.get_pipeline(pipeline_id)
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline with ID {pipeline_id} not found"
            )
        
        # Start execution (async task)
        job_id = await pipeline_service.execute_pipeline(pipeline_id, dataset_id)
        
        return {
            "status": "Pipeline execution started",
            "job_id": job_id,
            "pipeline_id": pipeline_id,
            "dataset_id": dataset_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing pipeline {pipeline_id} on dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/templates/{task_id}", response_model=PipelineResponse)
async def create_from_template(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new pipeline from a template for a specific ML task.
    """
    try:
        pipeline_service = PipelineService(db)
        new_pipeline = await pipeline_service.create_from_template(task_id)
        return new_pipeline
    except Exception as e:
        logger.error(f"Error creating pipeline from template: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 