from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..scraping.sources import scrape_all_sources

router = APIRouter(prefix="/api/scrape", tags=["Scraping"])


@router.post("/run")
def run_scraping(db: Session = Depends(get_db)):
    items = scrape_all_sources()
    created = 0
    for item in items:
        if item.url and crud.get_news_by_url(db, item.url):
            continue
        crud.create_news(db, item)
        created += 1
    return {"message": "Scraping selesai", "inserted": created}
