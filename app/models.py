from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from .database import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), index=True)
    url = Column(String(500), unique=True, index=True)
    title = Column(String(500))
    content = Column(Text)
    published_at = Column(DateTime, nullable=True)

    processed_text = Column(Text, nullable=True)
    topic_distribution = Column(Text, nullable=True)  # JSON string
    cluster_label = Column(Integer, nullable=True)
    recommended_title = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
