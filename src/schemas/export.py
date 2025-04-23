from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ExportBase(BaseModel):
    """Base export schema with common attributes."""
    job_id: int
    export_type: str = Field(..., description="Export format: 'huggingface', 'pytorch', 'tensorflow', 'csv', 'json'")
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class ExportCreate(ExportBase):
    """Schema for creating a new export."""
    pass

class ExportUpdate(BaseModel):
    """Schema for updating an existing export."""
    metadata: Optional[Dict[str, Any]] = None

class ExportResponse(ExportBase):
    """Schema for export response with additional fields."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ExportList(BaseModel):
    """Schema for a list of exports with pagination info."""
    exports: List[ExportResponse]
    total: int 