from typing import List
import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from sqlalchemy.orm import Session

from .. import crud, schemas, models
from ..database import get_db

router = APIRouter(prefix="/api/news", tags=["Manajemen Berita"])


@router.get("/", response_model=List[schemas.NewsOut])
def list_news(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_news(db, skip=skip, limit=limit)


@router.get("/page", response_model=schemas.NewsPage)
def list_news_page(
    skip: int = 0,
    limit: int = 20,
    cluster_label: int | None = None,
    has_recommendation: bool | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.News).order_by(models.News.created_at.desc())
    if cluster_label is not None:
        q = q.filter(models.News.cluster_label == cluster_label)
    if has_recommendation is True:
        q = q.filter(models.News.recommended_title.isnot(None))
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return schemas.NewsPage(items=items, total=total)


@router.post("/", response_model=schemas.NewsOut)
def create_news_item(news_in: schemas.NewsCreate, db: Session = Depends(get_db)):
    if news_in.url:
        existing = crud.get_news_by_url(db, url=news_in.url)
        if existing:
            raise HTTPException(status_code=400, detail="Berita dengan URL ini sudah ada")
    return crud.create_news(db, news_in)


@router.delete("/all")
def delete_all_news(db: Session = Depends(get_db)):
    deleted = crud.delete_all_news(db)
    return {"deleted": deleted}


@router.post("/upload-csv")
async def upload_news_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload berita dari file CSV.

    Kolom yang didukung (case-insensitive, boleh beberapa nama):
    - title / judul
    - content / isi
    - source / sumber
    - url / link
    - published_at / tanggal (ISO atau format umum: YYYY-MM-DD).
    """

    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File harus berformat CSV")

    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV kosong atau header tidak ditemukan")

    headers_norm = [h.lower() for h in reader.fieldnames if h]
    has_title = any(h in ("title", "judul") for h in headers_norm)
    has_content = any(h in ("content", "isi") for h in headers_norm)

    if not has_title or not has_content:
        raise HTTPException(
            status_code=400,
            detail=(
                "Format CSV tidak valid. Wajib ada kolom 'title' atau 'judul' dan 'content' atau 'isi'. "
                "Contoh header: title,content,source,url,published_at"
            ),
        )

    inserted = 0
    skipped = 0

    for row in reader:
        # normalisasi key ke lower untuk fleksibilitas
        norm = {k.lower(): v for k, v in row.items() if k is not None}

        title = norm.get("title") or norm.get("judul")
        content = norm.get("content") or norm.get("isi")

        if not title or not content:
            skipped += 1
            continue

        url = norm.get("url") or norm.get("link")
        source = norm.get("source") or norm.get("sumber")
        published_raw = norm.get("published_at") or norm.get("tanggal")

        published_at = None
        if published_raw:
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y"):
                try:
                    published_at = datetime.strptime(published_raw.strip(), fmt)
                    break
                except Exception:
                    continue

        if url and crud.get_news_by_url(db, url):
            skipped += 1
            continue

        news_in = schemas.NewsCreate(
            source=source,
            url=url,
            title=title,
            content=content,
            published_at=published_at,
        )

        crud.create_news(db, news_in)
        inserted += 1

    return {"inserted": inserted, "skipped": skipped}


@router.get("/csv-template")
def get_csv_template():
    content = "title,content,source,url,published_at\n" "Contoh judul,Contoh isi,sumber,https://contoh.com,2026-02-26\n"
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=news_template.csv"},
    )
