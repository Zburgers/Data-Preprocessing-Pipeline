from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
import importlib
import inspect
from abc import ABC, abstractmethod

from src.utils.logging import logger

class BaseStep(ABC):
    """
    Base class for all pipeline steps.
    
    Each step must implement the apply method, which transforms the data.
    """
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """
        Initialize the step with parameters.
        
        Args:
            params: Dictionary of parameters for this step
        """
        self.params = params or {}
        self._validate_params()
    
    @abstractmethod
    def _validate_params(self) -> None:
        """
        Validate the parameters for this step.
        
        Raises:
            ValueError: If parameters are invalid
        """
        pass
    
    @abstractmethod
    def apply(self, data: Any) -> Any:
        """
        Apply the transformation step to the input data.
        
        Args:
            data: Input data
            
        Returns:
            Transformed data
        """
        pass
    
    @classmethod
    def get_default_params(cls) -> Dict[str, Any]:
        """
        Get the default parameters for this step.
        
        Returns:
            Dictionary of default parameters
        """
        return {}
    
    @classmethod
    def get_param_schema(cls) -> Dict[str, Any]:
        """
        Get the parameter schema for this step.
        
        Returns:
            JSON Schema for parameters
        """
        return {
            "type": "object",
            "properties": {},
            "required": []
        }

class Pipeline:
    """
    Pipeline for data preprocessing.
    
    A pipeline consists of a sequence of steps that are applied to the data.
    """
    
    def __init__(self, steps: Optional[List[BaseStep]] = None):
        """
        Initialize the pipeline with steps.
        
        Args:
            steps: List of pipeline steps
        """
        self.steps = steps or []
    
    def add_step(self, step: BaseStep) -> None:
        """
        Add a step to the pipeline.
        
        Args:
            step: The step to add
        """
        self.steps.append(step)
    
    def process(self, data: Any) -> Any:
        """
        Process data through the pipeline.
        
        Args:
            data: Input data
            
        Returns:
            Processed data
        """
        result = data
        for i, step in enumerate(self.steps):
            logger.info(f"Applying step {i+1}/{len(self.steps)}: {step.__class__.__name__}")
            try:
                result = step.apply(result)
            except Exception as e:
                logger.error(f"Error in step {i+1}/{len(self.steps)}: {str(e)}")
                raise
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the pipeline to a dictionary representation.
        
        Returns:
            Dictionary representation of the pipeline
        """
        return {
            "steps": [
                {
                    "class": step.__class__.__name__,
                    "module": step.__class__.__module__,
                    "params": step.params
                }
                for step in self.steps
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pipeline':
        """
        Create a pipeline from a dictionary representation.
        
        Args:
            data: Dictionary representation of the pipeline
            
        Returns:
            Initialized pipeline
        """
        steps = []
        for step_data in data.get("steps", []):
            step_class_name = step_data.get("class")
            step_module_name = step_data.get("module")
            step_params = step_data.get("params", {})
            
            # Import the module and get the class
            try:
                module = importlib.import_module(step_module_name)
                step_class = getattr(module, step_class_name)
                step = step_class(step_params)
                steps.append(step)
            except (ImportError, AttributeError) as e:
                logger.error(f"Error loading step {step_class_name}: {str(e)}")
                raise
        
        return cls(steps)

class PipelineRegistry:
    """
    Registry for pipeline steps and templates.
    
    This class is responsible for discovering and registering steps and pipeline templates.
    """
    
    def __init__(self):
        """Initialize the registry."""
        self.steps: Dict[str, type] = {}
        self.templates: Dict[str, Dict[str, Any]] = {}
    
    def register_step(self, step_class: type) -> None:
        """
        Register a pipeline step class.
        
        Args:
            step_class: The step class to register
        """
        if not issubclass(step_class, BaseStep):
            raise TypeError(f"Step class {step_class.__name__} must inherit from BaseStep")
        
        self.steps[step_class.__name__] = step_class
        logger.info(f"Registered step: {step_class.__name__}")
    
    def register_template(self, name: str, template: Dict[str, Any]) -> None:
        """
        Register a pipeline template.
        
        Args:
            name: Template name
            template: Template configuration
        """
        self.templates[name] = template
        logger.info(f"Registered template: {name}")
    
    def get_step_class(self, name: str) -> type:
        """
        Get a registered step class by name.
        
        Args:
            name: Step class name
            
        Returns:
            The step class
            
        Raises:
            KeyError: If the step class is not registered
        """
        if name not in self.steps:
            raise KeyError(f"Step class {name} not registered")
        
        return self.steps[name]
    
    def get_template(self, name: str) -> Dict[str, Any]:
        """
        Get a registered template by name.
        
        Args:
            name: Template name
            
        Returns:
            The template configuration
            
        Raises:
            KeyError: If the template is not registered
        """
        if name not in self.templates:
            raise KeyError(f"Template {name} not registered")
        
        return self.templates[name]
    
    def discover_steps(self, package: str = "src.steps") -> None:
        """
        Discover and register steps in a package.
        
        Args:
            package: Package name to search
        """
        try:
            package_module = importlib.import_module(package)
            package_path = os.path.dirname(package_module.__file__)
            
            for module_info in os.listdir(package_path):
                # Skip __pycache__ and other non-module files
                if module_info.startswith("__") or not module_info.endswith(".py"):
                    continue
                
                module_name = f"{package}.{module_info[:-3]}"  # Remove .py extension
                
                try:
                    module = importlib.import_module(module_name)
                    # Find all classes in the module that are subclasses of BaseStep
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, BaseStep) and obj != BaseStep:
                            self.register_step(obj)
                except (ImportError, AttributeError) as e:
                    logger.error(f"Error loading module {module_name}: {str(e)}")
        except (ImportError, AttributeError) as e:
            logger.error(f"Error discovering steps in package {package}: {str(e)}")
    
    def discover_templates(self, templates_dir: str = "src/templates") -> None:
        """
        Discover and register templates in a directory.
        
        Args:
            templates_dir: Directory containing template files
        """
        templates_path = Path(templates_dir)
        if not templates_path.exists():
            logger.warning(f"Templates directory {templates_dir} does not exist")
            return
        
        for template_file in templates_path.glob("*.json"):
            try:
                with open(template_file, "r") as f:
                    template = json.load(f)
                
                template_name = template_file.stem
                self.register_template(template_name, template)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading template {template_file}: {str(e)}")

# Create global registry instance
registry = PipelineRegistry() 