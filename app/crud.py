from typing import Iterable, List, Optional

from sqlalchemy.orm import Session

from . import models, schemas


def get_news(db: Session, skip: int = 0, limit: int = 100) -> List[models.News]:
    return db.query(models.News).order_by(models.News.created_at.desc()).offset(skip).limit(limit).all()


def get_news_count(db: Session) -> int:
    return db.query(models.News).count()


def get_news_by_url(db: Session, url: str) -> Optional[models.News]:
    return db.query(models.News).filter(models.News.url == url).first()


def create_news(db: Session, news_in: schemas.NewsCreate) -> models.News:
    db_news = models.News(**news_in.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news


def bulk_create_news(db: Session, items: Iterable[schemas.NewsCreate]) -> int:
    objects = [models.News(**item.dict()) for item in items]
    db.add_all(objects)
    db.commit()
    return len(objects)


def delete_all_news(db: Session) -> int:
    """Hapus semua berita dari tabel news dan kembalikan jumlah baris terhapus."""
    deleted = db.query(models.News).delete()
    db.commit()
    return deleted


def update_news_analysis(
    db: Session,
    news_id: int,
    processed_text: Optional[str] = None,
    topic_distribution: Optional[str] = None,
    cluster_label: Optional[int] = None,
    recommended_title: Optional[str] = None,
) -> None:
    q = db.query(models.News).filter(models.News.id == news_id)
    updates = {}
    if processed_text is not None:
        updates["processed_text"] = processed_text
    if topic_distribution is not None:
        updates["topic_distribution"] = topic_distribution
    if cluster_label is not None:
        updates["cluster_label"] = cluster_label
    if recommended_title is not None:
        updates["recommended_title"] = recommended_title
    if updates:
        q.update(updates)
        db.commit()
