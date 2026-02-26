from collections import Counter
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(tags=["Dashboard"])


@router.get("/api/dashboard", response_model=schemas.DashboardSummary)
def get_dashboard_data(db: Session = Depends(get_db)):
    articles: List[models.News] = db.query(models.News).all()
    total = len(articles)

    cluster_counts = Counter([a.cluster_label for a in articles if a.cluster_label is not None])
    clusters = [
        {"cluster": int(k), "count": int(v)} for k, v in sorted(cluster_counts.items())
    ]

    timeline_counter: Counter[str] = Counter()
    for a in articles:
        dt: datetime | None = a.published_at or a.created_at
        key = dt.strftime("%Y-%m-%d")
        timeline_counter[key] += 1
    timeline = [
        {"date": k, "count": int(v)} for k, v in sorted(timeline_counter.items())
    ]

    topics = []

    return schemas.DashboardSummary(
        total_articles=total,
        topics=topics,
        clusters=clusters,
        timeline=timeline,
    )
