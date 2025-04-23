from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from src.services.database import Base, TimestampMixin

class PipelineStep(Base, TimestampMixin):
    """
    Pipeline Step model for storing metadata about available pipeline steps.
    """
    __tablename__ = "pipeline_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    step_type = Column(String(50), nullable=False)  # 'transform', 'filter', 'augment', etc.
    modality = Column(String(50), nullable=False)  # 'text', 'tabular', 'image', 'audio', 'video', 'multimodal'
    class_name = Column(String(100), nullable=False)  # The actual class implementing this step
    parameters = Column(JSON, nullable=True)  # Default parameters
    
    # Relationships
    configurations = relationship("PipelineConfiguration", back_populates="step", cascade="all, delete-orphan") 