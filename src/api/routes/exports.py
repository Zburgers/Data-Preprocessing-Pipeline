from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.schemas.export import ExportCreate, ExportResponse, ExportList
from src.services.database import get_db
from src.services.export_service import ExportService
from src.utils.logging import logger

router = APIRouter()

@router.post("/", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
async def create_export(
    export_data: ExportCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new export from a processed dataset.
    """
    try:
        export_service = ExportService(db)
        new_export = await export_service.create_export(export_data)
        return new_export
    except Exception as e:
        logger.error(f"Error creating export: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=ExportList)
async def list_exports(
    job_id: Optional[int] = None,
    export_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    List all available exports with optional filtering.
    """
    try:
        export_service = ExportService(db)
        exports = await export_service.get_exports(job_id=job_id, export_type=export_type, skip=skip, limit=limit)
        return {"exports": exports, "total": len(exports)}
    except Exception as e:
        logger.error(f"Error listing exports: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{export_id}", response_model=ExportResponse)
async def get_export(
    export_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific export by ID.
    """
    try:
        export_service = ExportService(db)
        export = await export_service.get_export(export_id)
        
        if not export:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Export with ID {export_id} not found"
            )
            
        return export
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving export {export_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{export_id}/download")
async def download_export(
    export_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Download an export file.
    """
    try:
        export_service = ExportService(db)
        export = await export_service.get_export(export_id)
        
        if not export:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Export with ID {export_id} not found"
            )
        
        file_path = export.file_path
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export file not found"
            )
        
        # This would need to be adjusted for S3/MinIO
        return await export_service.prepare_download(export_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading export {export_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{export_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_export(
    export_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an export by ID.
    """
    try:
        export_service = ExportService(db)
        success = await export_service.delete_export(export_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Export with ID {export_id} not found"
            )
            
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting export {export_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 