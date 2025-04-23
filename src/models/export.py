from sqlalchemy import Column, Integer, String, BigInteger, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.services.database import Base, TimestampMixin

class Export(Base, TimestampMixin):
    """
    Export model for tracking dataset exports.
    """
    __tablename__ = "exports"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    export_type = Column(String(50), nullable=False)  # 'huggingface', 'pytorch', 'tensorflow', 'csv', 'json'
    file_path = Column(String(255), nullable=True)  # S3/MinIO path
    file_size = Column(BigInteger, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    job = relationship("Job", back_populates="exports") 