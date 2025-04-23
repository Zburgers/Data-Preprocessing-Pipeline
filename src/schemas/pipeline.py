from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class PipelineBase(BaseModel):
    """Base pipeline schema with common attributes."""
    name: str
    description: Optional[str] = None
    ml_task_id: Optional[int] = None
    is_template: Optional[bool] = False
    configuration: Optional[Dict[str, Any]] = None

class PipelineCreate(PipelineBase):
    """Schema for creating a new pipeline."""
    pass

class PipelineUpdate(BaseModel):
    """Schema for updating an existing pipeline."""
    name: Optional[str] = None
    description: Optional[str] = None
    ml_task_id: Optional[int] = None
    configuration: Optional[Dict[str, Any]] = None

class PipelineStepConfig(BaseModel):
    """Schema for pipeline step configuration."""
    step_id: int
    order_index: int
    parameters: Optional[Dict[str, Any]] = None

class PipelineResponse(PipelineBase):
    """Schema for pipeline response with additional fields."""
    id: int
    created_at: datetime
    updated_at: datetime
    steps: Optional[List[PipelineStepConfig]] = None

    class Config:
        from_attributes = True

class PipelineList(BaseModel):
    """Schema for a list of pipelines with pagination info."""
    pipelines: List[PipelineResponse]
    total: int 