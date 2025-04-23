from typing import Dict, Any, Optional
import time
import os
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session

from src.tasks import app, task_context
from src.utils.logging import logger
from src.utils.db import get_sync_db
from src.models.dataset import Dataset
from src.detectors.modality_detector import DataModalityDetector
from src.detectors.task_detector import MLTaskDetector

@app.task(name="src.tasks.dataset_tasks.analyze_dataset_task")
def analyze_dataset_task(dataset_id: int) -> Dict[str, Any]:
    """
    Analyze a dataset to detect its modality, schema, and basic statistics.
    
    Args:
        dataset_id: ID of the dataset to analyze
        
    Returns:
        Dictionary with analysis results
    """
    with task_context("analyze_dataset"):
        # Get database session
        db = next(get_sync_db())
        
        try:
            # Get dataset
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                logger.error(f"Dataset not found: {dataset_id}")
                return {"status": "error", "message": f"Dataset not found: {dataset_id}"}
            
            # Check if file exists
            file_path = dataset.file_path
            if not os.path.exists(file_path):
                logger.error(f"Dataset file not found: {file_path}")
                return {"status": "error", "message": f"Dataset file not found: {file_path}"}
            
            # Detect modality
            modality_detector = DataModalityDetector()
            modality_info = modality_detector.detect(file_path)
            
            # Detect ML task
            task_detector = MLTaskDetector()
            task_info = task_detector.detect(file_path)
            
            # Collect basic statistics
            stats = collect_dataset_statistics(file_path, modality_info["modality"])
            
            # Update dataset with detected info
            dataset.modality = modality_info["modality"]
            if stats:
                if "row_count" in stats:
                    dataset.row_count = stats["row_count"]
                if "column_count" in stats:
                    dataset.column_count = stats["column_count"]
            
            # Store analysis results in metadata
            metadata = dataset.metadata or {}
            metadata.update({
                "analysis": {
                    "modality": modality_info,
                    "task": task_info,
                    "statistics": stats,
                    "analyzed_at": time.time()
                }
            })
            dataset.metadata = metadata
            
            # Commit changes
            db.commit()
            
            logger.info(f"Completed analysis for dataset {dataset_id}: {modality_info['modality']}")
            
            return {
                "status": "success",
                "dataset_id": dataset_id,
                "modality": modality_info,
                "task": task_info,
                "statistics": stats
            }
        
        except Exception as e:
            logger.error(f"Error analyzing dataset {dataset_id}: {str(e)}")
            return {"status": "error", "message": str(e)}
        
        finally:
            db.close()

def collect_dataset_statistics(file_path: str, modality: str) -> Optional[Dict[str, Any]]:
    """
    Collect basic statistics about a dataset.
    
    Args:
        file_path: Path to the dataset file
        modality: Detected modality of the dataset
        
    Returns:
        Dictionary with statistics, or None if not applicable
    """
    try:
        if modality == "tabular":
            # Determine file type from extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Load data
            if file_ext == ".csv":
                df = pd.read_csv(file_path)
            elif file_ext == ".tsv":
                df = pd.read_csv(file_path, sep="\t")
            elif file_ext == ".json":
                df = pd.read_json(file_path, lines=True)
            else:
                # Try to guess the format
                df = pd.read_csv(file_path, sep=None, engine="python")
            
            # Basic statistics
            stats = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": {}
            }
            
            # Column-level statistics
            for col in df.columns:
                col_stats = {
                    "dtype": str(df[col].dtype),
                    "missing_count": df[col].isnull().sum(),
                    "missing_percentage": round(df[col].isnull().mean() * 100, 2)
                }
                
                # Numeric column statistics
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_stats.update({
                        "min": float(df[col].min()) if not df[col].isnull().all() else None,
                        "max": float(df[col].max()) if not df[col].isnull().all() else None,
                        "mean": float(df[col].mean()) if not df[col].isnull().all() else None,
                        "median": float(df[col].median()) if not df[col].isnull().all() else None,
                        "std": float(df[col].std()) if not df[col].isnull().all() else None
                    })
                
                # Categorical column statistics
                elif pd.api.types.is_categorical_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]):
                    value_counts = df[col].value_counts().to_dict()
                    # Limit to top 10 values
                    if len(value_counts) > 10:
                        top_values = {k: v for k, v in sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:10]}
                        col_stats["top_values"] = top_values
                        col_stats["unique_count"] = len(value_counts)
                    else:
                        col_stats["values"] = value_counts
                
                stats["columns"][col] = col_stats
            
            return stats
        
        elif modality == "text":
            # Basic text file statistics
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Count lines, words, characters
            lines = content.split("\n")
            words = content.split()
            
            stats = {
                "line_count": len(lines),
                "word_count": len(words),
                "char_count": len(content)
            }
            
            return stats
        
        elif modality in ["image", "audio", "video"]:
            # File size and basic info
            stats = {
                "file_size_bytes": os.path.getsize(file_path)
            }
            
            # Additional modality-specific statistics could be added here
            # (e.g., image dimensions, audio duration, etc.)
            
            return stats
        
        else:
            # Generic file statistics
            return {
                "file_size_bytes": os.path.getsize(file_path)
            }
    
    except Exception as e:
        logger.error(f"Error collecting statistics for {file_path}: {str(e)}")
        return None 