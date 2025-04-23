from typing import Dict, Any, Optional, Union, List
import os
import pandas as pd
import numpy as np
import json
from pathlib import Path
import tempfile
import shutil

try:
    from datasets import Dataset, DatasetDict, Features, Value, ClassLabel
except ImportError:
    # Mock implementation if HuggingFace datasets is not installed
    Dataset = object
    DatasetDict = object
    Features = object
    Value = object
    ClassLabel = object

from src.exporters.base_exporter import BaseExporter
from src.utils.logging import logger

class HuggingFaceExporter(BaseExporter):
    """
    Exporter for HuggingFace datasets format.
    """
    
    def export(self, data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]], metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Export data to HuggingFace datasets format.
        
        Args:
            data: The data to export
            metadata: Optional metadata about the dataset
            
        Returns:
            Path to the exported data
        """
        try:
            # Ensure datasets library is available
            import datasets
        except ImportError:
            raise ImportError("HuggingFace datasets library is required for this exporter. Install with `pip install datasets`.")
        
        # Convert to DataFrame if not already
        if isinstance(data, pd.DataFrame):
            # Convert to dict of lists format
            data_dict = {col: data[col].tolist() for col in data.columns}
        elif isinstance(data, list):
            # Convert list of dicts to dict of lists
            if data and isinstance(data[0], dict):
                keys = data[0].keys()
                data_dict = {k: [d.get(k) for d in data] for k in keys}
            else:
                raise ValueError("Data format not supported. Expected list of dictionaries.")
        elif isinstance(data, dict):
            # Assume it's already in dict of lists format
            data_dict = data
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Try to infer features
        features = self._infer_features(data_dict, metadata)
        
        # Create HuggingFace Dataset
        dataset = datasets.Dataset.from_dict(data_dict, features=features)
        
        # If train/val/test split info is provided in metadata, create a DatasetDict
        if metadata and "splits" in metadata:
            splits = metadata["splits"]
            dataset_dict = self._create_dataset_splits(dataset, splits)
            
            # Save as DatasetDict
            dataset_path = os.path.join(self.output_dir, "dataset")
            dataset_dict.save_to_disk(dataset_path)
        else:
            # Save as single Dataset
            dataset_path = os.path.join(self.output_dir, "dataset")
            dataset.save_to_disk(dataset_path)
        
        # Save metadata if provided
        if metadata:
            self.save_metadata(metadata)
        
        logger.info(f"Exported data to HuggingFace dataset: {dataset_path}")
        return dataset_path
    
    def _infer_features(self, data_dict: Dict[str, List[Any]], metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Infer features for HuggingFace dataset.
        
        Args:
            data_dict: Dictionary of lists representing the dataset
            metadata: Optional metadata with feature information
            
        Returns:
            Features dict or None
        """
        try:
            import datasets
        except ImportError:
            return None
        
        # If feature info is provided in metadata, use it
        if metadata and "features" in metadata:
            feature_info = metadata["features"]
            features = {}
            
            for name, info in feature_info.items():
                if name not in data_dict:
                    continue
                    
                if info["type"] == "string":
                    features[name] = datasets.Value("string")
                elif info["type"] == "int":
                    features[name] = datasets.Value("int32")
                elif info["type"] == "float":
                    features[name] = datasets.Value("float32")
                elif info["type"] == "bool":
                    features[name] = datasets.Value("bool")
                elif info["type"] == "class_label" and "classes" in info:
                    features[name] = datasets.ClassLabel(names=info["classes"])
            
            return datasets.Features(features) if features else None
        
        # Otherwise, let HuggingFace infer features automatically
        return None
    
    def _create_dataset_splits(self, dataset, splits: Dict[str, Union[float, List[int]]]) -> 'DatasetDict':
        """
        Create train/val/test splits.
        
        Args:
            dataset: HuggingFace Dataset
            splits: Dictionary with split info
            
        Returns:
            DatasetDict with splits
        """
        try:
            import datasets
        except ImportError:
            raise ImportError("HuggingFace datasets library is required.")
        
        # If splits are provided as ratios (e.g., {"train": 0.8, "test": 0.2})
        if all(isinstance(v, float) for v in splits.values()):
            split_dataset = dataset.train_test_split(
                test_size=splits.get("test", 0.2),
                shuffle=True,
                seed=42
            )
            
            # If we need a validation split
            if "validation" in splits and "train" in split_dataset:
                train_val_split = split_dataset["train"].train_test_split(
                    test_size=splits["validation"] / (splits.get("train", 0.8)),
                    shuffle=True,
                    seed=42
                )
                return datasets.DatasetDict({
                    "train": train_val_split["train"],
                    "validation": train_val_split["test"],
                    "test": split_dataset["test"]
                })
            
            return split_dataset
        
        # If splits are provided as indices
        elif all(isinstance(v, list) for v in splits.values()):
            result = {}
            for split_name, indices in splits.items():
                result[split_name] = dataset.select(indices)
            
            return datasets.DatasetDict(result)
        
        else:
            raise ValueError("Splits must be either all ratios (float) or all indices (list of int).")
    
    @staticmethod
    def get_supported_modalities() -> List[str]:
        """
        Get the modalities supported by this exporter.
        
        Returns:
            List of supported modality strings
        """
        return ["tabular", "text", "image", "audio"] 