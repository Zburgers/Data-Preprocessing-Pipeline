from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from src.services.database import Base, TimestampMixin

class MLTask(Base, TimestampMixin):
    """
    ML Task model for storing metadata about supported machine learning tasks.
    """
    __tablename__ = "ml_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    modality = Column(String(50), nullable=False)  # 'text', 'tabular', 'image', 'audio', 'video', 'multimodal'
    task_type = Column(String(50), nullable=False)  # 'classification', 'regression', 'ner', 'object_detection', etc.
    
    # Relationships
    pipelines = relationship("Pipeline", back_populates="ml_task", cascade="all, delete-orphan") 