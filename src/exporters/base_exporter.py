from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
import shutil

from src.utils.logging import logger
from src.utils.config import settings

class BaseExporter(ABC):
    """
    Base class for dataset exporters.
    
    Exporters convert processed datasets to various formats for use in ML frameworks.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the exporter.
        
        Args:
            output_dir: Directory to save exported files. If None, a temp directory is created.
        """
        self.output_dir = output_dir or os.path.join(settings.UPLOAD_DIR, "exports", str(id(self)))
        os.makedirs(self.output_dir, exist_ok=True)
    
    @abstractmethod
    def export(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Export data to a specific format.
        
        Args:
            data: The data to export
            metadata: Optional metadata about the dataset
            
        Returns:
            Path to the exported data
        """
        pass
    
    def save_metadata(self, metadata: Dict[str, Any]) -> str:
        """
        Save metadata to a JSON file.
        
        Args:
            metadata: Metadata to save
            
        Returns:
            Path to the metadata file
        """
        metadata_path = os.path.join(self.output_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        return metadata_path
    
    def cleanup(self) -> None:
        """
        Clean up temporary files.
        """
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
    
    @staticmethod
    def get_supported_modalities() -> List[str]:
        """
        Get the modalities supported by this exporter.
        
        Returns:
            List of supported modality strings
        """
        return ["tabular", "text", "image", "audio", "video"] 