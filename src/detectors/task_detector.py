import os
import pandas as pd
import numpy as np
import json
import csv
from typing import Dict, List, Any, Optional, Union
from collections import Counter

from src.utils.logging import logger
from src.detectors.modality_detector import DataModalityDetector

class MLTaskDetector:
    """
    Detector for inferring the ML task type for a dataset.
    
    Supported task types:
    - classification: Binary or multi-class classification
    - regression: Numerical prediction
    - clustering: Unsupervised grouping
    - ner: Named Entity Recognition
    - object_detection: Object detection in images
    - image_classification: Image classification
    - audio_classification: Audio classification
    - text_generation: Text generation
    - translation: Translation
    - summarization: Text summarization
    """
    
    def __init__(self):
        """Initialize the detector."""
        self.modality_detector = DataModalityDetector()
    
    def detect(self, file_path: str, column_info: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Detect the ML task type for a dataset.
        
        Args:
            file_path: Path to the dataset file
            column_info: Optional dictionary mapping column names to their purpose
                (e.g., {"text": "input", "label": "target"})
            
        Returns:
            Dictionary with detected task type and confidence
        """
        # First, detect the modality
        modality_info = self.modality_detector.detect(file_path)
        modality = modality_info["modality"]
        
        # Detect task based on modality
        if modality == "tabular":
            return self._detect_tabular_task(file_path, column_info)
        elif modality == "text":
            return self._detect_text_task(file_path, column_info)
        elif modality == "image":
            return self._detect_image_task(file_path, column_info)
        elif modality == "audio":
            return self._detect_audio_task(file_path, column_info)
        elif modality == "video":
            return self._detect_video_task(file_path, column_info)
        else:
            return {
                "task_type": "unknown",
                "confidence": 0.0,
                "modality": modality
            }
    
    def _detect_tabular_task(self, file_path: str, column_info: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Detect the ML task type for a tabular dataset.
        
        Args:
            file_path: Path to the dataset file
            column_info: Optional dictionary mapping column names to their purpose
            
        Returns:
            Dictionary with detected task type and confidence
        """
        try:
            # Determine file type from extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Load a sample of the data to analyze
            if file_ext == ".csv":
                df = pd.read_csv(file_path, nrows=1000)
            elif file_ext == ".tsv":
                df = pd.read_csv(file_path, sep="\t", nrows=1000)
            elif file_ext == ".json":
                df = pd.read_json(file_path, lines=True, nrows=1000)
            else:
                # Try to guess the format
                df = pd.read_csv(file_path, nrows=1000, sep=None, engine="python")
            
            # If column_info is provided, use it to identify target column
            target_col = None
            if column_info:
                for col, purpose in column_info.items():
                    if purpose.lower() in ["target", "label", "class", "output"]:
                        target_col = col
                        break
            
            # If target column is not specified, try to guess based on column names
            if not target_col:
                for col in df.columns:
                    if col.lower() in ["target", "label", "class", "y", "output", "prediction"]:
                        target_col = col
                        break
            
            # If we have a target column, analyze its values
            if target_col and target_col in df.columns:
                # Count unique values in target column
                unique_count = df[target_col].nunique()
                total_count = len(df)
                
                # Check data type of target column
                if pd.api.types.is_numeric_dtype(df[target_col]):
                    # If few unique values relative to total count, likely classification
                    if unique_count < min(10, total_count * 0.05):
                        return {"task_type": "classification", "confidence": 0.8, "modality": "tabular"}
                    else:
                        return {"task_type": "regression", "confidence": 0.8, "modality": "tabular"}
                else:
                    # Categorical target, likely classification
                    return {"task_type": "classification", "confidence": 0.9, "modality": "tabular"}
            
            # If no target column identified, check for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                # Default to regression for numeric data without clear target
                return {"task_type": "regression", "confidence": 0.5, "modality": "tabular"}
            else:
                # Default to classification for non-numeric data
                return {"task_type": "classification", "confidence": 0.5, "modality": "tabular"}
        
        except Exception as e:
            logger.error(f"Error detecting tabular task: {str(e)}")
            return {"task_type": "unknown", "confidence": 0.0, "modality": "tabular"}
    
    def _detect_text_task(self, file_path: str, column_info: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Detect the ML task type for a text dataset.
        
        Args:
            file_path: Path to the dataset file
            column_info: Optional dictionary mapping column names to their purpose
            
        Returns:
            Dictionary with detected task type and confidence
        """
        try:
            # Check if it's a structured text file (JSON, CSV, etc.)
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in [".json", ".jsonl", ".csv", ".tsv"]:
                # Try to load as structured data
                return self._detect_tabular_task(file_path, column_info)
            
            # Raw text file analysis
            with open(file_path, "r", encoding="utf-8") as f:
                sample = f.read(10000)  # Read a sample
            
            # Check for patterns indicating NER (entities in [ENTITY] or <ENTITY> format)
            ner_patterns = ["[PERSON]", "[LOCATION]", "[ORGANIZATION]", "<PERSON>", "<LOCATION>", "<ORGANIZATION>"]
            if any(pattern in sample for pattern in ner_patterns):
                return {"task_type": "ner", "confidence": 0.7, "modality": "text"}
            
            # Check for patterns indicating translation (pairs of text separated by tabs or special markers)
            if "\t" in sample and sample.count("\n") > 0 and sample.count("\t") >= sample.count("\n"):
                return {"task_type": "translation", "confidence": 0.7, "modality": "text"}
            
            # Default to text classification
            return {"task_type": "text_classification", "confidence": 0.6, "modality": "text"}
        
        except Exception as e:
            logger.error(f"Error detecting text task: {str(e)}")
            return {"task_type": "unknown", "confidence": 0.0, "modality": "text"}
    
    def _detect_image_task(self, file_path: str, column_info: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Detect the ML task type for an image dataset.
        
        Args:
            file_path: Path to the dataset file
            column_info: Optional dictionary mapping column names to their purpose
            
        Returns:
            Dictionary with detected task type and confidence
        """
        # For single image files, default to image classification
        # In a real implementation, we'd look for annotation files or folder structure
        return {"task_type": "image_classification", "confidence": 0.7, "modality": "image"}
    
    def _detect_audio_task(self, file_path: str, column_info: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Detect the ML task type for an audio dataset.
        
        Args:
            file_path: Path to the dataset file
            column_info: Optional dictionary mapping column names to their purpose
            
        Returns:
            Dictionary with detected task type and confidence
        """
        # For single audio files, default to audio classification
        # In a real implementation, we'd look for annotation files or folder structure
        return {"task_type": "audio_classification", "confidence": 0.7, "modality": "audio"}
    
    def _detect_video_task(self, file_path: str, column_info: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Detect the ML task type for a video dataset.
        
        Args:
            file_path: Path to the dataset file
            column_info: Optional dictionary mapping column names to their purpose
            
        Returns:
            Dictionary with detected task type and confidence
        """
        # For single video files, default to video classification
        # In a real implementation, we'd look for annotation files or folder structure
        return {"task_type": "video_classification", "confidence": 0.7, "modality": "video"} 