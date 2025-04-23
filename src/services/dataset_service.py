from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import datetime

from src.models.dataset import Dataset
from src.schemas.dataset import DatasetCreate, DatasetUpdate
from src.utils.logging import logger
from src.tasks.dataset_tasks import analyze_dataset_task

class DatasetService:
    """
    Service for handling dataset operations.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db
    
    async def create_dataset(self, dataset_data: DatasetCreate) -> Dataset:
        """
        Create a new dataset in the database.
        
        Args:
            dataset_data: Dataset creation data
            
        Returns:
            The created dataset
        """
        # Create dataset model
        dataset = Dataset(
            name=dataset_data.name,
            description=dataset_data.description,
            source_type=dataset_data.source_type,
            modality=dataset_data.modality,
            file_path=dataset_data.file_path,
            file_size=dataset_data.file_size,
            file_type=dataset_data.file_type,
            row_count=dataset_data.row_count,
            column_count=dataset_data.column_count,
            metadata=dataset_data.metadata
        )
        
        # Add to database
        self.db.add(dataset)
        await self.db.commit()
        await self.db.refresh(dataset)
        
        # Log creation
        logger.info(f"Created dataset: {dataset.id} - {dataset.name}")
        
        return dataset
    
    async def get_dataset(self, dataset_id: int) -> Optional[Dataset]:
        """
        Get a dataset by ID.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            The dataset or None if not found
        """
        query = select(Dataset).where(Dataset.id == dataset_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_datasets(self, skip: int = 0, limit: int = 100) -> List[Dataset]:
        """
        Get a list of datasets with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of datasets
        """
        query = select(Dataset).offset(skip).limit(limit).order_by(Dataset.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_dataset(self, dataset_id: int, dataset_data: DatasetUpdate) -> Optional[Dataset]:
        """
        Update a dataset.
        
        Args:
            dataset_id: Dataset ID
            dataset_data: Dataset update data
            
        Returns:
            The updated dataset or None if not found
        """
        # Get dataset
        dataset = await self.get_dataset(dataset_id)
        if not dataset:
            return None
        
        # Update fields
        update_data = dataset_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(dataset, key, value)
        
        # Update timestamp
        dataset.updated_at = datetime.datetime.now()
        
        # Commit changes
        await self.db.commit()
        await self.db.refresh(dataset)
        
        # Log update
        logger.info(f"Updated dataset: {dataset.id} - {dataset.name}")
        
        return dataset
    
    async def delete_dataset(self, dataset_id: int) -> bool:
        """
        Delete a dataset.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            True if deleted, False if not found
        """
        # Get dataset
        dataset = await self.get_dataset(dataset_id)
        if not dataset:
            return False
        
        # Delete from database
        await self.db.delete(dataset)
        await self.db.commit()
        
        # Log deletion
        logger.info(f"Deleted dataset: {dataset_id}")
        
        return True
    
    async def analyze_dataset(self, dataset_id: int) -> bool:
        """
        Trigger analysis of a dataset.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            True if analysis task started, False if dataset not found
        """
        # Get dataset
        dataset = await self.get_dataset(dataset_id)
        if not dataset:
            return False
        
        # Trigger analysis task
        analyze_dataset_task.delay(dataset_id)
        
        # Log task creation
        logger.info(f"Started analysis task for dataset: {dataset_id}")
        
        return True 