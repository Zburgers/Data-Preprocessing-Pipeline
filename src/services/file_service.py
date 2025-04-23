import os
import uuid
import aiofiles
import boto3
import minio
from fastapi import UploadFile, HTTPException, status
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, BinaryIO
import shutil
import magic

from src.utils.config import settings
from src.utils.logging import logger

class FileService:
    """
    Service for handling file operations (upload, download, delete).
    Supports both local filesystem and S3-compatible storage.
    """
    
    def __init__(self):
        """Initialize the file service with the configured storage backend."""
        self.use_s3 = settings.USE_S3
        
        if self.use_s3:
            # Initialize S3 client
            self.s3_client = self._get_s3_client()
            # Ensure bucket exists
            self._ensure_bucket_exists()
        
        # Local upload directory
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_s3_client(self):
        """Get an S3 client using boto3."""
        if settings.S3_ENDPOINT and 'minio' in settings.S3_ENDPOINT.lower():
            # Use MinIO client for MinIO
            return minio.Minio(
                endpoint=settings.S3_ENDPOINT.replace('http://', '').replace('https://', ''),
                access_key=settings.S3_ACCESS_KEY,
                secret_key=settings.S3_SECRET_KEY,
                secure=settings.S3_ENDPOINT.startswith('https')
            )
        else:
            # Use boto3 for AWS S3 or other S3-compatible services
            return boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION
            )
    
    def _ensure_bucket_exists(self):
        """Ensure the specified S3 bucket exists."""
        try:
            if isinstance(self.s3_client, minio.Minio):
                if not self.s3_client.bucket_exists(settings.S3_BUCKET_NAME):
                    self.s3_client.make_bucket(settings.S3_BUCKET_NAME)
            else:
                # boto3 client
                self.s3_client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        except Exception as e:
            if isinstance(self.s3_client, minio.Minio):
                self.s3_client.make_bucket(settings.S3_BUCKET_NAME)
            else:
                self.s3_client.create_bucket(Bucket=settings.S3_BUCKET_NAME)
            logger.info(f"Created S3 bucket: {settings.S3_BUCKET_NAME}")
    
    def _validate_file(self, file: UploadFile) -> None:
        """
        Validate file type and size.
        
        Args:
            file: The file to validate
            
        Raises:
            HTTPException: If file validation fails
        """
        # Check file size
        if file.size and file.size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size ({file.size} bytes) exceeds maximum allowed size ({settings.MAX_UPLOAD_SIZE} bytes)"
            )
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File extension '{file_ext}' not allowed. Allowed extensions: {', '.join(settings.ALLOWED_UPLOAD_EXTENSIONS)}"
            )
    
    async def save_file(self, file: UploadFile, dataset_id: str) -> str:
        """
        Save an uploaded file to storage.
        
        Args:
            file: The uploaded file
            dataset_id: Unique identifier for the dataset
            
        Returns:
            str: The path/key where the file is stored
        """
        # Validate file
        self._validate_file(file)
        
        # Generate filename
        filename = file.filename
        file_ext = os.path.splitext(filename)[1].lower()
        unique_filename = f"{dataset_id}{file_ext}"
        
        if self.use_s3:
            # Save to S3
            return await self._save_to_s3(file, dataset_id, unique_filename)
        else:
            # Save to local filesystem
            return await self._save_to_local(file, dataset_id, unique_filename)
    
    async def _save_to_s3(self, file: UploadFile, dataset_id: str, filename: str) -> str:
        """Save file to S3 storage."""
        # Create key path
        key = f"raw/{dataset_id}/{filename}"
        
        # Create a temporary file
        temp_file_path = self.upload_dir / f"temp_{uuid.uuid4()}{os.path.splitext(filename)[1]}"
        try:
            # Save uploaded file to temp file
            async with aiofiles.open(temp_file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Upload to S3
            if isinstance(self.s3_client, minio.Minio):
                self.s3_client.fput_object(
                    bucket_name=settings.S3_BUCKET_NAME,
                    object_name=key,
                    file_path=str(temp_file_path),
                    content_type=file.content_type
                )
            else:
                with open(temp_file_path, 'rb') as f:
                    self.s3_client.upload_fileobj(
                        Fileobj=f,
                        Bucket=settings.S3_BUCKET_NAME,
                        Key=key,
                        ExtraArgs={'ContentType': file.content_type}
                    )
            
            logger.info(f"Uploaded file to S3: {key}")
            return key
        finally:
            # Clean up temp file
            if temp_file_path.exists():
                temp_file_path.unlink()
    
    async def _save_to_local(self, file: UploadFile, dataset_id: str, filename: str) -> str:
        """Save file to local filesystem."""
        # Create dataset directory
        dataset_dir = self.upload_dir / 'raw' / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # Create file path
        file_path = dataset_dir / filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"Saved file locally: {file_path}")
        return str(file_path)
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path or key of the file to delete
            
        Returns:
            bool: True if file was deleted, False if file was not found
        """
        if self.use_s3:
            # Delete from S3
            try:
                if isinstance(self.s3_client, minio.Minio):
                    self.s3_client.remove_object(settings.S3_BUCKET_NAME, file_path)
                else:
                    self.s3_client.delete_object(
                        Bucket=settings.S3_BUCKET_NAME,
                        Key=file_path
                    )
                logger.info(f"Deleted file from S3: {file_path}")
                return True
            except Exception as e:
                logger.error(f"Error deleting file from S3: {e}")
                return False
        else:
            # Delete from local filesystem
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Deleted file locally: {file_path}")
                return True
            return False
    
    async def get_file_stream(self, file_path: str) -> BinaryIO:
        """
        Get a file stream for reading.
        
        Args:
            file_path: Path or key of the file
            
        Returns:
            BinaryIO: File-like object
        """
        if self.use_s3:
            # Get from S3
            if isinstance(self.s3_client, minio.Minio):
                # Create a temporary file for MinIO
                temp_file_path = self.upload_dir / f"temp_{uuid.uuid4()}{os.path.splitext(file_path)[1]}"
                self.s3_client.fget_object(
                    bucket_name=settings.S3_BUCKET_NAME,
                    object_name=file_path,
                    file_path=str(temp_file_path)
                )
                return open(temp_file_path, 'rb')
            else:
                # Use boto3 streaming
                response = self.s3_client.get_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=file_path
                )
                return response['Body']
        else:
            # Get from local filesystem
            return open(file_path, 'rb') 