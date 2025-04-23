from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.services.database import Base, TimestampMixin

class Job(Base, TimestampMixin):
    """
    Job model for tracking pipeline execution jobs.
    """
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Will be a foreign key once we add user authentication
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
    status = Column(String(50), nullable=False)  # 'pending', 'processing', 'completed', 'failed'
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    result_path = Column(String(255), nullable=True)  # S3/MinIO path to the processed dataset
    job_metadata = Column(JSON, nullable=True)
    
    # Relationships
    dataset = relationship("Dataset", back_populates="jobs")
    pipeline = relationship("Pipeline", back_populates="jobs")
    exports = relationship("Export", back_populates="job", cascade="all, delete-orphan") 