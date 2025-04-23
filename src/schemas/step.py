from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class PipelineStepBase(BaseModel):
    """Base pipeline step schema with common attributes."""
    name: str
    description: Optional[str] = None
    step_type: str = Field(..., description="Step type: 'transform', 'filter', 'augment', etc.")
    modality: str = Field(..., description="Data modality: 'text', 'tabular', 'image', 'audio', 'video', 'multimodal'")
    class_name: str = Field(..., description="The actual class implementing this step")
    parameters: Optional[Dict[str, Any]] = None

class PipelineStepCreate(PipelineStepBase):
    """Schema for creating a new pipeline step."""
    pass

class PipelineStepUpdate(BaseModel):
    """Schema for updating an existing pipeline step."""
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class PipelineStepResponse(PipelineStepBase):
    """Schema for pipeline step response with additional fields."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PipelineStepList(BaseModel):
    """Schema for a list of pipeline steps with pagination info."""
    steps: List[PipelineStepResponse]
    total: int 