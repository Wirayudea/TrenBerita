import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models

router = APIRouter(prefix="/api/reports", tags=["Laporan"])


@router.get("/export")
def export_analysis_csv(db: Session = Depends(get_db)):
    """Export seluruh hasil analisis ke CSV.

    Kolom: id, source, url, title, content, published_at, processed_text,
    topic_distribution, cluster_label, recommended_title, created_at, updated_at.
    """

    articles = db.query(models.News).order_by(models.News.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    header = [
        "id",
        "source",
        "url",
        "title",
        "content",
        "published_at",
        "processed_text",
        "topic_distribution",
        "cluster_label",
        "recommended_title",
        "created_at",
        "updated_at",
    ]
    writer.writerow(header)

    for a in articles:
        def _fmt_dt(dt: datetime | None):
            return dt.isoformat() if dt else ""

        writer.writerow(
            [
                a.id,
                a.source or "",
                a.url or "",
                (a.title or "").replace("\n", " "),
                (a.content or "").replace("\n", " "),
                _fmt_dt(a.published_at),
                (a.processed_text or "").replace("\n", " "),
                a.topic_distribution or "",
                a.cluster_label if a.cluster_label is not None else "",
                (a.recommended_title or "").replace("\n", " "),
                _fmt_dt(a.created_at),
                _fmt_dt(a.updated_at),
            ]
        )

    csv_content = output.getvalue()
    filename = f"trenberita_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
