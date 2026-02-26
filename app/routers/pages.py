from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/manajemen-berita", response_class=HTMLResponse)
async def manajemen_berita(request: Request):
    return templates.TemplateResponse("news.html", {"request": request})


@router.get("/proses-analisis", response_class=HTMLResponse)
async def proses_analisis(request: Request):
    return templates.TemplateResponse("analysis.html", {"request": request})


@router.get("/hasil-topik", response_class=HTMLResponse)
async def hasil_topik(request: Request):
    return templates.TemplateResponse("topics.html", {"request": request})


@router.get("/hasil-clustering", response_class=HTMLResponse)
async def hasil_clustering(request: Request):
    return templates.TemplateResponse("clusters.html", {"request": request})


@router.get("/rekomendasi-judul", response_class=HTMLResponse)
async def rekomendasi_judul(request: Request):
    return templates.TemplateResponse("recommendations.html", {"request": request})


@router.get("/laporan", response_class=HTMLResponse)
async def laporan(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})
