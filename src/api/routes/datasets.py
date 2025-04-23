from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from src.schemas.dataset import DatasetCreate, DatasetResponse, DatasetList
from src.services.database import get_db
from src.services.dataset_service import DatasetService
from src.services.file_service import FileService
from src.utils.logging import logger

router = APIRouter()

@router.post("/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a new dataset file and create a dataset entry.
    """
    try:
        # Create a unique identifier for the dataset
        dataset_id = str(uuid.uuid4())
        
        # Save the file
        file_service = FileService()
        file_path = await file_service.save_file(file, dataset_id)
        
        # Create dataset entry
        dataset_service = DatasetService(db)
        dataset_data = DatasetCreate(
            name=name,
            description=description,
            source_type="upload",
            file_path=file_path,
            file_size=file.size,
            file_type=file.content_type
        )
        
        new_dataset = await dataset_service.create_dataset(dataset_data)
        
        # Trigger async analysis job
        # We'll implement this later
        
        return new_dataset
    except Exception as e:
        logger.error(f"Error creating dataset: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=DatasetList)
async def list_datasets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    List all available datasets with pagination.
    """
    try:
        dataset_service = DatasetService(db)
        datasets = await dataset_service.get_datasets(skip, limit)
        return {"datasets": datasets, "total": len(datasets)}
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific dataset by ID.
    """
    try:
        dataset_service = DatasetService(db)
        dataset = await dataset_service.get_dataset(dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID {dataset_id} not found"
            )
            
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a dataset by ID.
    """
    try:
        dataset_service = DatasetService(db)
        success = await dataset_service.delete_dataset(dataset_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID {dataset_id} not found"
            )
            
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{dataset_id}/analyze", response_model=dict)
async def analyze_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger analysis of a dataset to detect data type, schema, and statistics.
    """
    try:
        dataset_service = DatasetService(db)
        dataset = await dataset_service.get_dataset(dataset_id)
        
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID {dataset_id} not found"
            )
        
        # Trigger async analysis job
        # We'll implement this later
        
        return {"status": "Analysis job started", "dataset_id": dataset_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing dataset {dataset_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 