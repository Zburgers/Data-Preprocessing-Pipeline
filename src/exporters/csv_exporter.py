from typing import Dict, Any, Optional, Union, List
import os
import pandas as pd
import numpy as np
import json
from pathlib import Path

from src.exporters.base_exporter import BaseExporter
from src.utils.logging import logger

class CSVExporter(BaseExporter):
    """
    Exporter for CSV format.
    """
    
    def export(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Export data to CSV format.
        
        Args:
            data: The data to export
            metadata: Optional metadata about the dataset
            
        Returns:
            Path to the exported data
        """
        # Convert to DataFrame if not already
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Export to CSV
        csv_path = os.path.join(self.output_dir, "data.csv")
        data.to_csv(csv_path, index=False)
        
        # Save metadata if provided
        if metadata:
            self.save_metadata(metadata)
        
        logger.info(f"Exported data to CSV: {csv_path}")
        return csv_path
    
    @staticmethod
    def get_supported_modalities() -> List[str]:
        """
        Get the modalities supported by this exporter.
        
        Returns:
            List of supported modality strings
        """
        return ["tabular", "text"] 