from dataclasses import dataclass
from datetime import datetime
from typing import List
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from ..schemas import NewsCreate


@dataclass
class ScrapedItem:
    source: str
    url: str
    title: str
    content: str
    published_at: datetime | None = None


HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TrenBeritaBot/0.1)"}


def _scrape_generic_tag(base_url: str, source_name: str, limit: int = 15) -> List[ScrapedItem]:
    """Scraper generic untuk halaman tag.

    Pendekatan aman: ambil sejumlah kecil link artikel dari domain yg sama,
    lalu ambil seluruh <p> sebagai isi konten.
    """

    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    base_host = urlparse(base_url).netloc

    links: List[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if not text:
            continue
        if href.startswith("/"):
            href = urljoin(base_url, href)
        if not href.startswith("http"):
            continue

        host = urlparse(href).netloc
        if base_host not in host:
            continue

        if href not in links:
            links.append(href)
        if len(links) >= limit:
            break

    items: List[ScrapedItem] = []
    for url in links:
        try:
            art_resp = requests.get(url, headers=HEADERS, timeout=10)
            art_resp.raise_for_status()
            art_soup = BeautifulSoup(art_resp.text, "html.parser")

            paragraphs = [p.get_text(strip=True) for p in art_soup.find_all("p")]
            content = "\n".join([p for p in paragraphs if p])

            title_tag = art_soup.find("h1") or art_soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else url

            if not content or not title:
                continue

            items.append(
                ScrapedItem(
                    source=source_name,
                    url=url,
                    title=title,
                    content=content,
                )
            )
        except Exception:
            continue

    return items


def scrape_detik_viral() -> List[ScrapedItem]:
    base_url = "https://www.detik.com/tag/viral"
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    items: List[ScrapedItem] = []

    for a in soup.select("article a[href]")[:20]:
        url = a["href"]
        title = a.get_text(strip=True)
        if not url or not title:
            continue
        try:
            art_resp = requests.get(url, headers=HEADERS, timeout=10)
            art_resp.raise_for_status()
            art_soup = BeautifulSoup(art_resp.text, "html.parser")
            paragraphs = [p.get_text(strip=True) for p in art_soup.select("article p")]
            content = "\n".join(paragraphs)
            if not content:
                continue
            items.append(ScrapedItem(source="detik", url=url, title=title, content=content))
        except Exception:
            continue

    return items

def scrape_okezone_viral() -> List[ScrapedItem]:
    return _scrape_generic_tag("https://www.okezone.com/tag/viral", "okezone")


def scrape_antaranews_viral() -> List[ScrapedItem]:
    return _scrape_generic_tag("https://m.antaranews.com/tag/viral", "antaranews")


def scrape_viralsumsel() -> List[ScrapedItem]:
    return _scrape_generic_tag("https://www.viralsumsel.com/", "viralsumsel")


def scrape_detik_sumsel() -> List[ScrapedItem]:
    return _scrape_generic_tag("https://www.detik.com/tag/sumatera-selatan", "detik-sumsel")


def scrape_cnn_viral() -> List[ScrapedItem]:
    base_url = "https://www.cnnindonesia.com/tag/viral"
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    links: List[str] = []
    # Heuristik: link artikel biasanya mengandung segmen tahun /202x/ dalam path
    for a in soup.select("a[href]"):
        href = a.get("href") or ""
        if not href.startswith("https://www.cnnindonesia.com/"):
            continue
        if "/202" not in href:
            continue
        if href not in links:
            links.append(href)
        if len(links) >= 15:
            break

    items: List[ScrapedItem] = []
    for url in links:
        try:
            art_resp = requests.get(url, headers=HEADERS, timeout=10)
            art_resp.raise_for_status()
            art_soup = BeautifulSoup(art_resp.text, "html.parser")

            paragraphs = [p.get_text(strip=True) for p in art_soup.select("article p")]
            if not paragraphs:
                paragraphs = [p.get_text(strip=True) for p in art_soup.find_all("p")]
            content = "\n".join([p for p in paragraphs if p])

            title_tag = art_soup.find("h1") or art_soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else url

            if not content or not title:
                continue

            items.append(
                ScrapedItem(
                    source="cnnindonesia",
                    url=url,
                    title=title,
                    content=content,
                )
            )
        except Exception:
            continue

    return items


def scrape_tribun_sumsel() -> List[ScrapedItem]:
    base_url = "https://sumsel.tribunnews.com/"
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    links: List[str] = []
    for a in soup.select("a[href]"):
        href = a.get("href") or ""
        if not href.startswith("https://sumsel.tribunnews.com/"):
            continue
        parsed = urlparse(href)
        parts = [p for p in parsed.path.split("/") if p]
        # Heuristik: url berita mengandung segmen angka id, mis. /palembang/1008283/...
        has_numeric_segment = any(part.isdigit() and len(part) >= 5 for part in parts)
        if not has_numeric_segment:
            continue
        if href not in links:
            links.append(href)
        if len(links) >= 15:
            break

    items: List[ScrapedItem] = []
    for url in links:
        try:
            art_resp = requests.get(url, headers=HEADERS, timeout=10)
            art_resp.raise_for_status()
            art_soup = BeautifulSoup(art_resp.text, "html.parser")

            paragraphs = [p.get_text(strip=True) for p in art_soup.select("#article-body p")]
            if not paragraphs:
                paragraphs = [p.get_text(strip=True) for p in art_soup.select("article p")]
            if not paragraphs:
                paragraphs = [p.get_text(strip=True) for p in art_soup.find_all("p")]
            content = "\n".join([p for p in paragraphs if p])

            title_tag = art_soup.find("h1") or art_soup.find("title")
            title = title_tag.get_text(strip=True) if title_tag else url

            if not content or not title:
                continue

            items.append(
                ScrapedItem(
                    source="tribun-sumsel",
                    url=url,
                    title=title,
                    content=content,
                )
            )
        except Exception:
            continue

    return items


def scrape_all_sources() -> List[NewsCreate]:
    scraped: List[ScrapedItem] = []

    for fn in (
        scrape_detik_viral,
        scrape_okezone_viral,
        scrape_cnn_viral,
        scrape_tribun_sumsel,
        # scrape_antaranews_viral,
        # scrape_viralsumsel,
        # scrape_detik_sumsel,
    ):
        try:
            scraped.extend(fn())
        except Exception:
            continue

    result: List[NewsCreate] = []
    seen_urls: set[str] = set()

    for item in scraped:
        if item.url in seen_urls:
            continue
        seen_urls.add(item.url)
        result.append(
            NewsCreate(
                source=item.source,
                url=item.url,
                title=item.title,
                content=item.content,
                published_at=item.published_at,
            )
        )
    return result
