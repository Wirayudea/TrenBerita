from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class NewsBase(BaseModel):
    source: Optional[str] = None
    url: Optional[str] = None
    title: str
    content: str
    published_at: Optional[datetime] = None


class NewsCreate(NewsBase):
    pass


class NewsOut(NewsBase):
    id: int
    processed_text: Optional[str] = None
    topic_distribution: Optional[str] = None
    cluster_label: Optional[int] = None
    recommended_title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardSummary(BaseModel):
    total_articles: int
    topics: list
    clusters: list
    timeline: list


class NewsPage(BaseModel):
    items: List[NewsOut]
    total: int
