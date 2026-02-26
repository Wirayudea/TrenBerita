import json
from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, models
from ..database import get_db
from ..nlp.clustering import KMeansClusterer
from ..nlp.lda_model import LDAModeler
from ..nlp.preprocessing import preprocess
from ..nlp.recommender import generate_title_from_keywords

router = APIRouter(prefix="/api/analysis", tags=["Proses Analisis"])


_lda_model: LDAModeler | None = None
_clusterer: KMeansClusterer | None = None
_topics_cache: List[Dict] | None = None


@router.post("/run")
def run_full_analysis(n_topics: int = 5, n_clusters: int = 5, db: Session = Depends(get_db)):
    global _lda_model, _clusterer, _topics_cache

    articles: List[models.News] = db.query(models.News).all()
    if not articles:
        return {"message": "Tidak ada berita untuk dianalisis"}

    docs = []
    for a in articles:
        processed = preprocess(a.content or "")
        docs.append(processed)
        crud.update_news_analysis(db, a.id, processed_text=processed)

    _lda_model = LDAModeler(n_topics=n_topics)
    topic_distributions = _lda_model.fit_transform(docs)
    _topics_cache = _lda_model.get_topics(top_n=10)

    _clusterer = KMeansClusterer(n_clusters=n_clusters)
    labels = _clusterer.fit_predict(topic_distributions)

    for art, dist, label in zip(articles, topic_distributions, labels):
        topic_dist_json = LDAModeler.serialize_distribution(dist)
        top_topic_idx = int(dist.argmax())
        keywords = [term for term, _ in _topics_cache[top_topic_idx]["terms"][:6]] if _topics_cache else []
        rec_title = generate_title_from_keywords(keywords)

        crud.update_news_analysis(
            db,
            art.id,
            topic_distribution=topic_dist_json,
            cluster_label=label,
            recommended_title=rec_title,
        )

    return {
        "message": "Analisis selesai",
        "total_articles": len(articles),
        "n_topics": n_topics,
        "n_clusters": n_clusters,
    }


@router.get("/topics")
def get_topics():
    if not _topics_cache:
        return []
    return _topics_cache
