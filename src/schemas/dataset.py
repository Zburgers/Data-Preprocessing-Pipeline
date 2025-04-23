from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DatasetBase(BaseModel):
    """Base dataset schema with common attributes."""
    name: str
    description: Optional[str] = None
    source_type: str = Field(..., description="Source of the dataset: 'upload', 'api', 'scheduled'")
    modality: Optional[str] = Field(None, description="Data modality: 'text', 'tabular', 'image', 'audio', 'video', 'multimodal'")
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    row_count: Optional[int] = None
    column_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class DatasetCreate(DatasetBase):
    """Schema for creating a new dataset."""
    pass

class DatasetUpdate(BaseModel):
    """Schema for updating an existing dataset."""
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DatasetResponse(DatasetBase):
    """Schema for dataset response with additional fields."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DatasetList(BaseModel):
    """Schema for a list of datasets with pagination info."""
    datasets: List[DatasetResponse]
    total: int 