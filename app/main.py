from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from . import models
from .routers import analysis, dashboard, news, pages, scrape, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Analisis Tren Berita Online")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages.router)
app.include_router(news.router)
app.include_router(scrape.router)
app.include_router(analysis.router)
app.include_router(dashboard.router)
app.include_router(reports.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
