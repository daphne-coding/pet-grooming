"""Generate static GitHub Pages for each pet grooming store.

This script reads the source CSV files in the repository root and builds
individual store pages plus an index landing page under ``docs/`` so they can
be published with GitHub Pages ("Deploy from a /docs folder").
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = ROOT / "google-2025-12-28.csv"
DETAIL_CSV = ROOT / "寵物美容detail.csv"
DOCS_DIR = ROOT / "docs"
ASSETS_DIR = DOCS_DIR / "assets"
STORES_DIR = DOCS_DIR / "stores"
DATA_DIR = DOCS_DIR / "data"


@dataclass
class Store:
    slug: str
    name: str
    map_url: str
    rating: float | None
    review_count: int | None
    category: str | None
    address: str | None
    status: str | None
    hours_note: str | None
    website: str | None
    phone: str | None
    services: list[str]
    image_url: str | None

    def badge_text(self) -> str:
        pieces: list[str] = []
        if self.category:
            pieces.append(self.category)
        if self.status:
            pieces.append(self.status)
        if self.hours_note:
            pieces.append(self.hours_note)
        return " · ".join(pieces)


def load_images() -> dict[str, str]:
    images: dict[str, str] = {}
    with DETAIL_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader, None)  # header
        for row in reader:
            if len(row) < 2:
                continue
            map_url, image_url = row[0].strip(), row[1].strip()
            if map_url and image_url:
                images[map_url] = image_url
    return images


def coerce_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def coerce_int(value: str) -> int | None:
    digits = re.sub(r"[^0-9]", "", value)
    return int(digits) if digits else None


def clean_text(value: str | None) -> str | None:
    if not value:
        return None
    stripped = value.strip().lstrip("⋅").strip()
    return stripped or None


def parse_stores(image_lookup: dict[str, str]) -> list[Store]:
    stores: list[Store] = []
    with DATA_CSV.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader, None)  # header row
        for row in reader:
            if len(row) < 3:
                continue
            map_url = row[1].strip()
            name = row[2].strip()
            if not (map_url and name and map_url.startswith("http")):
                continue

            rating = coerce_float(row[3].strip()) if len(row) > 3 else None
            review_count = coerce_int(row[4]) if len(row) > 4 else None
            category = clean_text(row[5] if len(row) > 5 else None)
            address = clean_text(row[7] if len(row) > 7 else None)
            status = clean_text(row[8] if len(row) > 8 else None)
            hours_note = clean_text(row[9] if len(row) > 9 else None)
            website_raw = row[10].strip() if len(row) > 10 else ""
            website = website_raw if website_raw.startswith("http") else None
            phone = clean_text(row[16] if len(row) > 16 else None)

            services: list[str] = []
            for chunk in row[17:]:
                text = clean_text(chunk)
                if text and text != "·":
                    services.append(text)

            slug = f"store-{len(stores) + 1:02d}"
            image_url = image_lookup.get(map_url)

            stores.append(
                Store(
                    slug=slug,
                    name=name,
                    map_url=map_url,
                    rating=rating,
                    review_count=review_count,
                    category=category,
                    address=address,
                    status=status,
                    hours_note=hours_note,
                    website=website,
                    phone=phone,
                    services=services,
                    image_url=image_url,
                )
            )
    return stores


def write_json(stores: Iterable[Store]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = [store.__dict__ for store in stores]
    (DATA_DIR / "stores.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_assets() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    # The stylesheet lives in version control; this ensures the directory exists
    # when the script is run in isolation.


def render_index(stores: list[Store]) -> str:
    cards = "\n".join(render_card(store) for store in stores)
    return f"""<!doctype html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>台中寵物美容地圖｜獨立店家網站索引</title>
  <link rel=\"stylesheet\" href=\"assets/style.css\" />
</head>
<body>
  <header class=\"hero\">
    <div class=\"container\">
      <p class=\"eyebrow\">GitHub Pages 專案</p>
      <h1>台中寵物美容店家索引</h1>
      <p class=\"lede\">每間店都有自己的介紹頁面、地圖連結與聯絡資訊。點擊下方卡片即可瀏覽。</p>
    </div>
  </header>
  <main class=\"container\">
    <section class=\"grid\">{cards}</section>
  </main>
  <footer class=\"footer\">
    <div class=\"container\">
      <p>資料來源：repo 內建 CSV，網站自動生成，可直接透過 GitHub Pages 發佈。</p>
    </div>
  </footer>
</body>
</html>
"""


def render_card(store: Store) -> str:
    image = escape(store.image_url or "https://via.placeholder.com/640x360?text=Pet+Grooming")
    badge = escape(store.badge_text())
    rating = f"{store.rating:.1f}" if store.rating is not None else "--"
    reviews = f"（{store.review_count} 則評論）" if store.review_count is not None else ""
    address = escape(store.address or "地址未提供")
    return f"""
      <article class=\"card\">
        <a class=\"card__link\" href=\"stores/{store.slug}/index.html\">
          <div class=\"card__image\">
            <img src=\"{image}\" alt=\"{escape(store.name)}\" loading=\"lazy\" />
          </div>
          <div class=\"card__body\">
            <p class=\"badge\">{badge or '寵物美容'}</p>
            <h2 class=\"card__title\">{escape(store.name)}</h2>
            <p class=\"card__meta\">⭐ {rating} {reviews}</p>
            <p class=\"card__text\">{address}</p>
          </div>
        </a>
      </article>
    """


def render_store(store: Store) -> str:
    image = escape(store.image_url or "https://via.placeholder.com/960x540?text=Pet+Grooming")
    rating = f"{store.rating:.1f}" if store.rating is not None else "--"
    reviews = f"（{store.review_count} 則評論）" if store.review_count is not None else ""
    services = "".join(f"<li>{escape(item)}</li>" for item in store.services) or "<li>歡迎電話洽詢服務內容</li>"
    address = escape(store.address or "地址未提供")
    status_line = escape(store.status or "營業狀態未提供")
    hours_line = escape(store.hours_note or "歡迎電話詢問營業時間")
    website_link = f"<a class=\"button\" href=\"{escape(store.website)}\" target=\"_blank\" rel=\"noopener\">造訪官方網站</a>" if store.website else ""
    phone_line = f"<a class=\"button button--ghost\" href=\"tel:{escape(store.phone)}\">撥打 {escape(store.phone)} </a>" if store.phone else ""
    map_link = escape(store.map_url)

    return f"""<!doctype html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{escape(store.name)}｜台中寵物美容店</title>
  <link rel=\"stylesheet\" href=\"../../assets/style.css\" />
</head>
<body>
  <header class=\"hero\">
    <div class=\"container\">
      <p class=\"eyebrow\">獨立店家頁面</p>
      <h1>{escape(store.name)}</h1>
      <p class=\"lede\">{escape(store.badge_text() or '提供專業寵物美容服務')}</p>
      <div class=\"actions\">
        <a class=\"button\" href=\"{map_link}\" target=\"_blank\" rel=\"noopener\">查看地圖 / 導航</a>
        {website_link}
        {phone_line}
        <a class=\"button button--ghost\" href=\"../../index.html\">回到店家索引</a>
      </div>
    </div>
  </header>
  <main class=\"container layout\">
    <div class=\"layout__media\">
      <img src=\"{image}\" alt=\"{escape(store.name)}\" />
    </div>
    <div class=\"layout__content\">
      <div class=\"pill\">⭐ {rating} {reviews}</div>
      <p class=\"detail\"><strong>地址：</strong>{address}</p>
      <p class=\"detail\"><strong>營業狀態：</strong>{status_line}</p>
      <p class=\"detail\"><strong>營業時間：</strong>{hours_line}</p>
      <p class=\"detail\"><strong>聯絡電話：</strong>{escape(store.phone) if store.phone else '未提供'}</p>
      <p class=\"detail\"><strong>地圖連結：</strong><a href=\"{map_link}\" target=\"_blank\" rel=\"noopener\">在地圖上查看</a></p>
      <h2>服務與備註</h2>
      <ul class=\"list\">{services}</ul>
    </div>
  </main>
  <footer class=\"footer\">
    <div class=\"container\">
      <p>此頁面由 CSV 自動生成，可直接透過 GitHub Pages 發佈。</p>
    </div>
  </footer>
</body>
</html>
"""


def generate_pages() -> None:
    image_lookup = load_images()
    stores = parse_stores(image_lookup)
    if not stores:
        raise SystemExit("No stores found to generate")

    ensure_assets()
    STORES_DIR.mkdir(parents=True, exist_ok=True)

    write_json(stores)

    # Index
    (DOCS_DIR / "index.html").write_text(render_index(stores), encoding="utf-8")

    # Individual store pages
    for store in stores:
        store_dir = STORES_DIR / store.slug
        store_dir.mkdir(parents=True, exist_ok=True)
        (store_dir / "index.html").write_text(render_store(store), encoding="utf-8")


if __name__ == "__main__":
    generate_pages()
