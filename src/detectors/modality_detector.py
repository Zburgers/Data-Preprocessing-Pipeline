import os
import mimetypes
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import magic
import json
import csv

from src.utils.logging import logger

class DataModalityDetector:
    """
    Detector for inferring the modality of a dataset.
    
    Supported modalities:
    - text: Plain text, CSV with text data, JSON with text data
    - tabular: CSV, TSV, Excel, etc. with structured data
    - image: JPEG, PNG, GIF, etc.
    - audio: WAV, MP3, etc.
    - video: MP4, AVI, etc.
    - multimodal: Dataset with multiple modalities
    """
    
    # MIME type mappings to modalities
    MIME_MODALITY_MAP = {
        # Text
        "text/plain": "text",
        "text/csv": "tabular",
        "text/tab-separated-values": "tabular",
        "application/json": "text",  # Further analysis needed
        
        # Images
        "image/jpeg": "image",
        "image/png": "image",
        "image/gif": "image",
        "image/bmp": "image",
        "image/tiff": "image",
        "image/webp": "image",
        
        # Audio
        "audio/wav": "audio",
        "audio/x-wav": "audio",
        "audio/mpeg": "audio",
        "audio/mp3": "audio",
        "audio/ogg": "audio",
        "audio/flac": "audio",
        
        # Video
        "video/mp4": "video",
        "video/x-msvideo": "video",  # AVI
        "video/quicktime": "video",  # MOV
        "video/x-matroska": "video",  # MKV
        "video/webm": "video",
        
        # PDF (requires further analysis)
        "application/pdf": "document",
        
        # Archives (requires further analysis)
        "application/zip": "archive",
        "application/x-tar": "archive",
        "application/x-gzip": "archive"
    }
    
    # File extension mappings to modalities
    EXT_MODALITY_MAP = {
        # Text and tabular
        ".txt": "text",
        ".csv": "tabular",
        ".tsv": "tabular",
        ".json": "text",  # Further analysis needed
        ".jsonl": "text",  # Further analysis needed
        ".xml": "text",
        
        # Images
        ".jpg": "image",
        ".jpeg": "image",
        ".png": "image",
        ".gif": "image",
        ".bmp": "image",
        ".tiff": "image",
        ".webp": "image",
        
        # Audio
        ".wav": "audio",
        ".mp3": "audio",
        ".ogg": "audio",
        ".flac": "audio",
        ".m4a": "audio",
        
        # Video
        ".mp4": "video",
        ".avi": "video",
        ".mov": "video",
        ".mkv": "video",
        ".webm": "video",
        
        # Documents
        ".pdf": "document",
        
        # Archives
        ".zip": "archive",
        ".tar": "archive",
        ".gz": "archive"
    }
    
    def __init__(self):
        """Initialize the detector."""
        # Initialize mime types
        mimetypes.init()
    
    def detect(self, file_path: str) -> Dict[str, Any]:
        """
        Detect the modality of a dataset.
        
        Args:
            file_path: Path to the dataset file
            
        Returns:
            Dictionary with detected modality and confidence
        """
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Detect MIME type
        mime_type = self._get_mime_type(file_path)
        
        # Initial guess based on MIME type and extension
        modality = self._guess_modality(mime_type, file_ext)
        
        # Refine guess with content analysis
        if modality in ["text", "tabular", "document"]:
            modality = self._analyze_text_content(file_path, file_ext, modality)
        elif modality == "archive":
            modality = "multimodal"  # Archives likely contain multiple file types
        
        return {
            "modality": modality,
            "confidence": 0.9,  # Placeholder, would be calculated based on analysis
            "mime_type": mime_type,
            "file_ext": file_ext
        }
    
    def _get_mime_type(self, file_path: str) -> str:
        """
        Get the MIME type of a file using python-magic.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type string
        """
        try:
            mime = magic.Magic(mime=True)
            return mime.from_file(file_path)
        except Exception as e:
            logger.warning(f"Error detecting MIME type with python-magic: {str(e)}")
            # Fallback to mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type or "application/octet-stream"
    
    def _guess_modality(self, mime_type: str, file_ext: str) -> str:
        """
        Make an initial guess of modality based on MIME type and file extension.
        
        Args:
            mime_type: MIME type string
            file_ext: File extension
            
        Returns:
            Modality string
        """
        # Try MIME type first
        if mime_type in self.MIME_MODALITY_MAP:
            return self.MIME_MODALITY_MAP[mime_type]
        
        # Try file extension
        if file_ext in self.EXT_MODALITY_MAP:
            return self.EXT_MODALITY_MAP[file_ext]
        
        # Default to unknown
        return "unknown"
    
    def _analyze_text_content(self, file_path: str, file_ext: str, initial_modality: str) -> str:
        """
        Analyze text content to determine if it's text or tabular.
        
        Args:
            file_path: Path to the file
            file_ext: File extension
            initial_modality: Initial modality guess
            
        Returns:
            Refined modality string
        """
        # For JSON files, check structure
        if file_ext == ".json":
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                # Check if it's an array of objects (likely tabular)
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                    return "tabular"
                # Check if it's a nested object (likely complex data)
                elif isinstance(data, dict) and any(isinstance(v, (dict, list)) for v in data.values()):
                    return "multimodal"
                # Otherwise, probably just text
                else:
                    return "text"
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON file: {file_path}")
                return initial_modality
        
        # For CSV/TSV files, check if it has a header and multiple columns
        elif file_ext in [".csv", ".tsv"]:
            try:
                delimiter = "," if file_ext == ".csv" else "\t"
                with open(file_path, "r") as f:
                    sample = f.read(4096)  # Read a sample
                
                # Count commas and tabs to determine structure
                if sample.count(delimiter) > (2 * sample.count("\n")):
                    return "tabular"  # Multiple columns per line
                else:
                    return "text"  # Probably just text with occasional delimiters
            except Exception as e:
                logger.warning(f"Error analyzing CSV/TSV: {str(e)}")
                return initial_modality
        
        # For text files, check if it looks like CSV
        elif file_ext == ".txt":
            try:
                with open(file_path, "r") as f:
                    sample = f.read(4096)  # Read a sample
                
                # Count commas, tabs, and pipes to determine if it's structured
                if (sample.count(",") > (2 * sample.count("\n")) or
                    sample.count("\t") > (2 * sample.count("\n")) or
                    sample.count("|") > (2 * sample.count("\n"))):
                    return "tabular"  # Multiple delimiters per line
                else:
                    return "text"  # Just text
            except Exception as e:
                logger.warning(f"Error analyzing TXT: {str(e)}")
                return initial_modality
        
        return initial_modality 