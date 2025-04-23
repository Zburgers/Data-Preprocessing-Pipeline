import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, LabelEncoder

from src.pipeline_engine import BaseStep
from src.utils.logging import logger

class MissingValueImputer(BaseStep):
    """
    Step for imputing missing values in tabular data.
    """
    
    def _validate_params(self) -> None:
        """Validate parameters."""
        valid_strategies = ["mean", "median", "most_frequent", "constant"]
        if "strategy" in self.params and self.params["strategy"] not in valid_strategies:
            raise ValueError(f"Invalid strategy: {self.params['strategy']}. Must be one of {valid_strategies}")
        
        if "columns" in self.params and not isinstance(self.params["columns"], list):
            raise ValueError("columns parameter must be a list")
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply missing value imputation to the input data.
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame with imputed values
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input data must be a pandas DataFrame")
        
        # Make a copy to avoid modifying the original
        result = data.copy()
        
        # Get parameters
        strategy = self.params.get("strategy", "mean")
        fill_value = self.params.get("fill_value", 0)  # Only used for constant strategy
        columns = self.params.get("columns", None)  # If None, apply to all numeric columns
        
        # Select columns to impute
        if columns:
            # Filter to only include columns that exist in the data
            cols_to_impute = [col for col in columns if col in result.columns]
        else:
            # Select numeric columns
            cols_to_impute = result.select_dtypes(include=["number"]).columns.tolist()
        
        if not cols_to_impute:
            logger.warning("No columns to impute")
            return result
        
        # Initialize imputer
        imputer = SimpleImputer(
            strategy=strategy,
            fill_value=fill_value if strategy == "constant" else None
        )
        
        # Apply imputation
        result[cols_to_impute] = imputer.fit_transform(result[cols_to_impute])
        
        logger.info(f"Imputed missing values in {len(cols_to_impute)} columns using {strategy} strategy")
        return result
    
    @classmethod
    def get_default_params(cls) -> Dict[str, Any]:
        """Get default parameters."""
        return {
            "strategy": "mean",
            "fill_value": 0,
            "columns": None
        }
    
    @classmethod
    def get_param_schema(cls) -> Dict[str, Any]:
        """Get parameter schema."""
        return {
            "type": "object",
            "properties": {
                "strategy": {
                    "type": "string",
                    "enum": ["mean", "median", "most_frequent", "constant"],
                    "description": "Strategy for imputing missing values"
                },
                "fill_value": {
                    "type": "number",
                    "description": "Value to use when strategy is 'constant'"
                },
                "columns": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                    "description": "Columns to impute (null for all numeric columns)"
                }
            }
        }

class NumericScaler(BaseStep):
    """
    Step for scaling numeric columns in tabular data.
    """
    
    def _validate_params(self) -> None:
        """Validate parameters."""
        valid_scalers = ["standard", "minmax", "robust", "none"]
        if "scaler" in self.params and self.params["scaler"] not in valid_scalers:
            raise ValueError(f"Invalid scaler: {self.params['scaler']}. Must be one of {valid_scalers}")
        
        if "columns" in self.params and not isinstance(self.params["columns"], list):
            raise ValueError("columns parameter must be a list")
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply scaling to numeric columns.
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame with scaled values
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input data must be a pandas DataFrame")
        
        # Make a copy to avoid modifying the original
        result = data.copy()
        
        # Get parameters
        scaler_type = self.params.get("scaler", "standard")
        columns = self.params.get("columns", None)  # If None, apply to all numeric columns
        
        # If no scaling requested, return the original data
        if scaler_type == "none":
            return result
        
        # Select columns to scale
        if columns:
            # Filter to only include columns that exist in the data
            cols_to_scale = [col for col in columns if col in result.columns]
        else:
            # Select numeric columns
            cols_to_scale = result.select_dtypes(include=["number"]).columns.tolist()
        
        if not cols_to_scale:
            logger.warning("No columns to scale")
            return result
        
        # Initialize scaler
        if scaler_type == "standard":
            scaler = StandardScaler()
        elif scaler_type == "minmax":
            scaler = MinMaxScaler()
        elif scaler_type == "robust":
            from sklearn.preprocessing import RobustScaler
            scaler = RobustScaler()
        
        # Apply scaling
        result[cols_to_scale] = scaler.fit_transform(result[cols_to_scale])
        
        logger.info(f"Scaled {len(cols_to_scale)} columns using {scaler_type} scaler")
        return result
    
    @classmethod
    def get_default_params(cls) -> Dict[str, Any]:
        """Get default parameters."""
        return {
            "scaler": "standard",
            "columns": None
        }
    
    @classmethod
    def get_param_schema(cls) -> Dict[str, Any]:
        """Get parameter schema."""
        return {
            "type": "object",
            "properties": {
                "scaler": {
                    "type": "string",
                    "enum": ["standard", "minmax", "robust", "none"],
                    "description": "Type of scaler to use"
                },
                "columns": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                    "description": "Columns to scale (null for all numeric columns)"
                }
            }
        }

class CategoricalEncoder(BaseStep):
    """
    Step for encoding categorical columns in tabular data.
    """
    
    def _validate_params(self) -> None:
        """Validate parameters."""
        valid_encoders = ["onehot", "label", "none"]
        if "encoder" in self.params and self.params["encoder"] not in valid_encoders:
            raise ValueError(f"Invalid encoder: {self.params['encoder']}. Must be one of {valid_encoders}")
        
        if "columns" in self.params and not isinstance(self.params["columns"], list):
            raise ValueError("columns parameter must be a list")
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply encoding to categorical columns.
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame with encoded values
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input data must be a pandas DataFrame")
        
        # Make a copy to avoid modifying the original
        result = data.copy()
        
        # Get parameters
        encoder_type = self.params.get("encoder", "onehot")
        columns = self.params.get("columns", None)  # If None, apply to all categorical columns
        
        # If no encoding requested, return the original data
        if encoder_type == "none":
            return result
        
        # Select columns to encode
        if columns:
            # Filter to only include columns that exist in the data
            cols_to_encode = [col for col in columns if col in result.columns]
        else:
            # Select categorical and object columns
            cols_to_encode = result.select_dtypes(include=["category", "object"]).columns.tolist()
        
        if not cols_to_encode:
            logger.warning("No columns to encode")
            return result
        
        # Apply encoding
        if encoder_type == "onehot":
            # One-hot encode each column
            for col in cols_to_encode:
                # Convert to pandas categorical first for efficiency
                if not pd.api.types.is_categorical_dtype(result[col]):
                    result[col] = result[col].astype("category")
                
                # Create dummy variables
                dummies = pd.get_dummies(result[col], prefix=col)
                
                # Add to result and drop original column
                result = pd.concat([result, dummies], axis=1)
                result = result.drop(col, axis=1)
        
        elif encoder_type == "label":
            # Label encode each column
            for col in cols_to_encode:
                encoder = LabelEncoder()
                result[col] = encoder.fit_transform(result[col].astype(str))
        
        logger.info(f"Encoded {len(cols_to_encode)} columns using {encoder_type} encoder")
        return result
    
    @classmethod
    def get_default_params(cls) -> Dict[str, Any]:
        """Get default parameters."""
        return {
            "encoder": "onehot",
            "columns": None
        }
    
    @classmethod
    def get_param_schema(cls) -> Dict[str, Any]:
        """Get parameter schema."""
        return {
            "type": "object",
            "properties": {
                "encoder": {
                    "type": "string",
                    "enum": ["onehot", "label", "none"],
                    "description": "Type of encoder to use"
                },
                "columns": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                    "description": "Columns to encode (null for all categorical columns)"
                }
            }
        }

class OutlierHandler(BaseStep):
    """
    Step for handling outliers in tabular data.
    """
    
    def _validate_params(self) -> None:
        """Validate parameters."""
        valid_methods = ["clip", "remove", "none"]
        if "method" in self.params and self.params["method"] not in valid_methods:
            raise ValueError(f"Invalid method: {self.params['method']}. Must be one of {valid_methods}")
        
        if "columns" in self.params and not isinstance(self.params["columns"], list):
            raise ValueError("columns parameter must be a list")
    
    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply outlier handling to the input data.
        
        Args:
            data: Input DataFrame
            
        Returns:
            DataFrame with handled outliers
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input data must be a pandas DataFrame")
        
        # Make a copy to avoid modifying the original
        result = data.copy()
        
        # Get parameters
        method = self.params.get("method", "clip")
        columns = self.params.get("columns", None)  # If None, apply to all numeric columns
        threshold = self.params.get("threshold", 3.0)  # Number of standard deviations
        
        # If no outlier handling requested, return the original data
        if method == "none":
            return result
        
        # Select columns to process
        if columns:
            # Filter to only include columns that exist in the data
            cols_to_process = [col for col in columns if col in result.columns]
        else:
            # Select numeric columns
            cols_to_process = result.select_dtypes(include=["number"]).columns.tolist()
        
        if not cols_to_process:
            logger.warning("No columns to process for outliers")
            return result
        
        # Handle outliers
        if method == "clip":
            # Clip values outside the threshold
            for col in cols_to_process:
                mean = result[col].mean()
                std = result[col].std()
                lower_bound = mean - threshold * std
                upper_bound = mean + threshold * std
                result[col] = result[col].clip(lower=lower_bound, upper=upper_bound)
        
        elif method == "remove":
            # Remove rows with values outside the threshold
            for col in cols_to_process:
                mean = result[col].mean()
                std = result[col].std()
                lower_bound = mean - threshold * std
                upper_bound = mean + threshold * std
                result = result[(result[col] >= lower_bound) & (result[col] <= upper_bound)]
        
        logger.info(f"Handled outliers in {len(cols_to_process)} columns using {method} method")
        return result
    
    @classmethod
    def get_default_params(cls) -> Dict[str, Any]:
        """Get default parameters."""
        return {
            "method": "clip",
            "threshold": 3.0,
            "columns": None
        }
    
    @classmethod
    def get_param_schema(cls) -> Dict[str, Any]:
        """Get parameter schema."""
        return {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "enum": ["clip", "remove", "none"],
                    "description": "Method for handling outliers"
                },
                "threshold": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Number of standard deviations to use as threshold"
                },
                "columns": {
                    "type": ["array", "null"],
                    "items": {"type": "string"},
                    "description": "Columns to process (null for all numeric columns)"
                }
            }
        } 