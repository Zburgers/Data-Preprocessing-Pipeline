from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class MLTaskBase(BaseModel):
    """Base ML task schema with common attributes."""
    name: str
    description: Optional[str] = None
    modality: str = Field(..., description="Data modality: 'text', 'tabular', 'image', 'audio', 'video', 'multimodal'")
    task_type: str = Field(..., description="ML task type: 'classification', 'regression', 'ner', 'object_detection', etc.")

class MLTaskCreate(MLTaskBase):
    """Schema for creating a new ML task."""
    pass

class MLTaskUpdate(BaseModel):
    """Schema for updating an existing ML task."""
    name: Optional[str] = None
    description: Optional[str] = None

class MLTaskResponse(MLTaskBase):
    """Schema for ML task response with additional fields."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MLTaskList(BaseModel):
    """Schema for a list of ML tasks with pagination info."""
    tasks: List[MLTaskResponse]
    total: int 