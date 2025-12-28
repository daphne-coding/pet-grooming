from __future__ import annotations
import csv
import html
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

DATA_FILE = Path("google-2025-12-28.csv")
DETAIL_FILE = Path("寵物美容detail.csv")
OUTPUT_DIR = Path("docs")
ASSETS_DIR = OUTPUT_DIR / "assets"

@dataclass
class Store:
    name: str
    map_url: str
    rating: Optional[str]
    review_count: Optional[str]
    category: Optional[str]
    address: Optional[str]
    status: Optional[str]
    hours: Optional[str]
    website: Optional[str]
    phone: Optional[str]
    features: List[str] = field(default_factory=list)
    image_url: Optional[str] = None
    slug: str = ""


def slugify(name: str, existing: set[str]) -> str:
    base = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", name).strip("-").lower()
    if not base:
        base = "store"
    slug = base
    counter = 2
    while slug in existing:
        slug = f"{base}-{counter}"
        counter += 1
    existing.add(slug)
    return slug


def load_images() -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    if not DETAIL_FILE.exists():
        return mapping
    with DETAIL_FILE.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            map_url = row.get("hfpxzc href", "").strip()
            img = row.get("aoRNLd src", "").strip()
            if map_url and img:
                mapping[map_url] = img
    return mapping


def clean_value(text: str) -> str:
    return text.replace("⋅", "").replace("·", "").strip()


def load_stores() -> List[Store]:
    images = load_images()
    stores: List[Store] = []
    seen_slugs: set[str] = set()

    with DATA_FILE.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("qBF1Pd", "").strip()
            map_url = row.get("hfpxzc href", "").strip()
            if not name:
                continue

            store = Store(
                name=name,
                map_url=map_url,
                rating=clean_value(row.get("MW4etd", "")),
                review_count=clean_value(row.get("UY7F9", "").strip("()")),
                category=clean_value(row.get("W4Efsd", "")),
                address=clean_value(row.get("W4Efsd (3)", "")),
                status=clean_value(row.get("W4Efsd (4)", "")),
                hours=clean_value(row.get("W4Efsd (5)", "")),
                website=row.get("lcr4fd href", "").strip() or None,
                phone=clean_value(row.get("UsdlK", "")) or None,
            )

            for key in ["ah5Ghc", "ah5Ghc (2)"]:
                value = clean_value(row.get(key, ""))
                if value:
                    store.features.append(value)

            store.image_url = images.get(map_url)
            store.slug = slugify(store.name, seen_slugs)
            stores.append(store)

    return stores


def ensure_assets():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    style_path = ASSETS_DIR / "style.css"
    if not style_path.exists():
        style_path.write_text(
            (
                "@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;600;700&display=swap');\n"
                ":root{--bg:#f8fafc;--card:#ffffff;--accent:#ff9f43;--text:#0f172a;--muted:#475569;--border:#e2e8f0;}\n"
                "*{box-sizing:border-box;}body{margin:0;font-family:'Noto Sans TC',system-ui,sans-serif;background:var(--bg);color:var(--text);}"
                "a{text-decoration:none;color:inherit;}\n"
                "header{padding:32px 24px 16px;max-width:1080px;margin:auto;}\n"
                "h1,h2,h3{margin:0 0 12px;font-weight:700;line-height:1.2;}\n"
                "p{margin:0 0 12px;color:var(--muted);}\n"
                ".chip{display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:999px;border:1px solid var(--border);background:#fff;}\n"
                ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;padding:0 24px 32px;max-width:1080px;margin:auto;}\n"
                ".card{background:var(--card);border:1px solid var(--border);border-radius:16px;overflow:hidden;display:flex;flex-direction:column;transition:transform .15s ease,box-shadow .15s ease;}\n"
                ".card:hover{transform:translateY(-3px);box-shadow:0 10px 30px rgba(15,23,42,.1);}\n"
                ".thumb{height:160px;background:linear-gradient(120deg,#ffe4c4,#ffd0a8);position:relative;}\n"
                ".thumb img{width:100%;height:100%;object-fit:cover;display:block;}\n"
                ".card-body{padding:16px;display:flex;flex-direction:column;gap:8px;}\n"
                ".meta{display:flex;flex-wrap:wrap;gap:8px;color:var(--muted);font-size:14px;}\n"
                ".button-row{display:flex;flex-wrap:wrap;gap:10px;margin-top:4px;}\n"
                ".button{padding:10px 12px;border-radius:10px;border:1px solid var(--border);background:#fff;font-weight:600;display:inline-flex;gap:6px;align-items:center;}\n"
                ".button.primary{background:var(--accent);color:#1f2937;border:none;}\n"
                ".layout{max-width:920px;margin:auto;padding:0 24px 40px;}\n"
                ".hero{background:var(--card);border-bottom:1px solid var(--border);padding:28px 24px 16px;}\n"
                ".section{margin-top:24px;padding:20px;border-radius:14px;background:var(--card);border:1px solid var(--border);}\n"
                ".info-list{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;}\n"
                ".info-item{padding:12px;border-radius:12px;border:1px dashed var(--border);background:#fdfdfd;}\n"
                ".badge{display:inline-block;padding:6px 10px;border-radius:8px;background:rgba(255,159,67,.15);color:#c05d00;font-weight:600;margin-right:8px;}\n"
            ),
            encoding="utf-8",
        )


def render_index(stores: List[Store]):
    OUTPUT_DIR.mkdir(exist_ok=True)
    ensure_assets()
    cards = []
    for store in stores:
        display_name = store.name.rstrip("|｜") or store.name
        image_tag = (
            f"<img src='{html.escape(store.image_url)}' alt='{html.escape(store.name)}'>"
            if store.image_url
            else ""
        )
        card_parts = [
            "<article class='card'>",
            f"<div class='thumb'>{image_tag}</div>",
            "<div class='card-body'>",
            f"<a href='{store.slug}/index.html'><h3>{html.escape(display_name)}</h3></a>",
            "<div class='meta'>",
            f"<span>⭐ {html.escape(store.rating or '尚無評分')}</span>",
        ]
        if store.review_count:
            card_parts.append(f"<span>({html.escape(store.review_count)} 則評論)</span>")
        if store.category:
            card_parts.append(f"<span>{html.escape(store.category)}</span>")

        card_parts.extend(
            [
                "</div>",
                f"<p>{html.escape(store.address or '地址未提供')}</p>",
                "<div class='button-row'>",
                f"<a class='button primary' href='{html.escape(store.map_url)}' target='_blank' rel='noreferrer'>查看地圖</a>",
            ]
        )
        if store.website:
            card_parts.append(
                f"<a class='button' href='{html.escape(store.website)}' target='_blank' rel='noreferrer'>官方網站</a>"
            )
        card_parts.extend(["</div>", "</div></article>"])

        cards.append("".join(card_parts))

    index_html = f"""<!doctype html>
<html lang='zh-Hant'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>寵物美容店家索引</title>
  <link rel='stylesheet' href='assets/style.css'>
</head>
<body>
  <header>
    <p class='chip'>GitHub Pages · 寵物美容</p>
    <h1>寵物美容店家索引</h1>
    <p>為您整理台中多家寵物美容與自助洗澡店家的基本資訊，點擊卡片即可查看專屬分頁。</p>
  </header>
  <section class='grid'>
    {''.join(cards)}
  </section>
</body>
</html>"""
    (OUTPUT_DIR / "index.html").write_text(index_html, encoding="utf-8")


def render_store_page(store: Store):
    OUTPUT_DIR.mkdir(exist_ok=True)
    ensure_assets()
    store_dir = OUTPUT_DIR / store.slug
    store_dir.mkdir(parents=True, exist_ok=True)
    display_name = store.name.rstrip("|｜") or store.name

    meta_items = []
    if store.address:
        meta_items.append(f"<li class='info-item'><strong>地址</strong><br>{html.escape(store.address)}</li>")
    if store.phone:
        meta_items.append(f"<li class='info-item'><strong>電話</strong><br>{html.escape(store.phone)}</li>")
    if store.status:
        meta_items.append(f"<li class='info-item'><strong>營業狀態</strong><br>{html.escape(store.status)}</li>")
    if store.hours:
        meta_items.append(f"<li class='info-item'><strong>營業時間</strong><br>{html.escape(store.hours)}</li>")

    features_html = "".join(
        f"<span class='badge'>{html.escape(feature)}</span>" for feature in store.features
    )

    image_block = (
        f"<div class='thumb'><img src='{html.escape(store.image_url)}' alt='{html.escape(display_name)}'></div>"
        if store.image_url
        else "<div class='thumb'></div>"
    )

    store_html = f"""<!doctype html>
<html lang='zh-Hant'>
  <head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>{html.escape(display_name)}｜寵物美容店家</title>
    <link rel='stylesheet' href='../assets/style.css'>
  </head>
  <body>
    <div class='hero'>
      <a class='chip' href='../index.html'>← 返回列表</a>
      <h1>{html.escape(display_name)}</h1>
      <p class='meta'>
        <span>⭐ {html.escape(store.rating or '尚無評分')}</span>
        {f"<span>({html.escape(store.review_count)} 則評論)</span>" if store.review_count else ''}
        {f"<span>{html.escape(store.category)}</span>" if store.category else ''}
      </p>
    </div>
    <div class='layout'>
      <div class='section'>
        {image_block}
        <div class='button-row' style='margin-top:12px;'>
          <a class='button primary' href='{html.escape(store.map_url)}' target='_blank' rel='noreferrer'>在地圖查看</a>
          {f"<a class='button' href='{html.escape(store.website)}' target='_blank' rel='noreferrer'>官方網站</a>" if store.website else ''}
        </div>
        {f"<div style='margin-top:12px;'>{features_html}</div>" if features_html else ''}
      </div>

      <div class='section'>
        <h2>店家資訊</h2>
        <ul class='info-list'>
          {''.join(meta_items)}
        </ul>
      </div>
    </div>
  </body>
</html>"""

    (store_dir / "index.html").write_text(store_html, encoding="utf-8")


def build_site():
    stores = load_stores()
    render_index(stores)
    for store in stores:
        render_store_page(store)
    print(f"Generated {len(stores)} store pages in {OUTPUT_DIR}/")


if __name__ == "__main__":
    build_site()
