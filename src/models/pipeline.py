from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.services.database import Base, TimestampMixin

class Pipeline(Base, TimestampMixin):
    """
    Pipeline model for storing metadata about data preprocessing pipelines.
    """
    __tablename__ = "pipelines"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Will be a foreign key once we add user authentication
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    ml_task_id = Column(Integer, ForeignKey("ml_tasks.id"), nullable=True)
    is_template = Column(Boolean, default=False)
    configuration = Column(JSON, nullable=True)
    
    # Relationships
    ml_task = relationship("MLTask", back_populates="pipelines")
    steps = relationship("PipelineConfiguration", back_populates="pipeline", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="pipeline", cascade="all, delete-orphan")

class PipelineConfiguration(Base, TimestampMixin):
    """
    Pipeline Configuration model for storing the steps in a pipeline.
    """
    __tablename__ = "pipeline_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
    step_id = Column(Integer, ForeignKey("pipeline_steps.id"), nullable=False)
    order_index = Column(Integer, nullable=False)
    parameters = Column(JSON, nullable=True)
    
    # Relationships
    pipeline = relationship("Pipeline", back_populates="steps")
    step = relationship("PipelineStep", back_populates="configurations") 