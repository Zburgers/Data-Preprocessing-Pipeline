from sqlalchemy import Column, Integer, String, Text, BigInteger, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.services.database import Base, TimestampMixin

class Dataset(Base, TimestampMixin):
    """
    Dataset model for storing metadata about uploaded datasets.
    """
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Will be a foreign key once we add user authentication
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    source_type = Column(String(50), nullable=False)  # 'upload', 'api', 'scheduled'
    modality = Column(String(50), nullable=True)  # 'text', 'tabular', 'image', 'audio', 'video', 'multimodal'
    file_path = Column(String(255), nullable=True)
    file_size = Column(BigInteger, nullable=True)
    file_type = Column(String(50), nullable=True)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    jobs = relationship("Job", back_populates="dataset", cascade="all, delete-orphan") 