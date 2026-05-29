"""Static-site export for Cloudflare Pages.

Pre-renders every public route to ``dist/`` so the read-only site can be served
as plain files — no Python server, no cold starts, global CDN. Run this AFTER
the data-compute steps so the rendered pages embed the fresh numbers.

    python -m scripts.build_static            # -> ./dist

Deterministic and free: it just drives the existing FastAPI app through
Starlette's TestClient and saves what each route returns. Nothing here calls an
LLM or hits a paid API.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import (  # noqa: E402
    app,
    _all_pair_slugs,
    _load_research_posts,
    _PAIR_PRIORITY,
)

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
STATIC_SRC = ROOT / "app" / "static"


def _write(rel: str, text: str) -> None:
    p = DIST / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _page(client: TestClient, url: str, out_rel: str) -> None:
    """Fetch an HTML/XML/text route and save it; fail loudly on a bad status."""
    r = client.get(url)
    if r.status_code != 200:
        raise RuntimeError(f"{url} -> HTTP {r.status_code} (refusing to publish a broken page)")
    _write(out_rel, r.text)


def build() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    client = TestClient(app)

    posts = _load_research_posts()
    codes = [c.lower() for c in _PAIR_PRIORITY]
    pairs = _all_pair_slugs()

    # --- Clean-URL HTML pages -> <path>/index.html ---
    _page(client, "/", "index.html")
    _page(client, "/about", "about/index.html")
    _page(client, "/research", "research/index.html")
    _page(client, "/privacy", "privacy/index.html")
    for p in posts:
        _page(client, f"/research/{p['slug']}", f"research/{p['slug']}/index.html")
    for c in codes:
        _page(client, f"/currency/{c}", f"currency/{c}/index.html")
    for slug in pairs:
        _page(client, f"/pair/{slug}", f"pair/{slug}/index.html")

    # --- Machine endpoints ---
    _page(client, "/sitemap.xml", "sitemap.xml")
    _page(client, "/robots.txt", "robots.txt")

    # --- Public JSON API as static files (.json so the CDN sets the type) ---
    r = client.get("/api/strength")
    if r.status_code == 200:
        _write("api/strength.json", r.text)
    for c in [x.upper() for x in _PAIR_PRIORITY]:
        rr = client.get(f"/api/strength/{c}")
        if rr.status_code == 200:
            _write(f"api/strength/{c.lower()}.json", rr.text)

    # --- Static assets (css/js/img/fonts) ---
    shutil.copytree(STATIC_SRC, DIST / "static")

    # --- Cloudflare _redirects: legacy URLs + reverse-order pair slugs ---
    lines = [
        "/strength / 301",
        "/run / 301",
        "/run/* / 301",
    ]
    for slug in pairs:                       # /pair/usdeur -> /pair/eurusd, etc.
        rev = slug[3:] + slug[:3]
        if rev != slug:
            lines.append(f"/pair/{rev} /pair/{slug} 301")
    _write("_redirects", "\n".join(lines) + "\n")

    total = sum(1 for _ in DIST.rglob("*") if _.is_file())
    print(f"static build -> {DIST}  ({total} files)")
    print(f"  pages: 4 base + {len(posts)} research + {len(codes)} currency + {len(pairs)} pair")


if __name__ == "__main__":
    build()
