"""Fetch the latest FOMC and ECB statements and write them to
data/fomc_latest.txt and data/ecb_latest.txt.

Run after each meeting:
    .venv/Scripts/python.exe scripts/fetch_central_bank_statements.py

Or schedule it the morning after each known FOMC / ECB Governing
Council meeting. Both pages are static once published, so re-running
is idempotent.

Approach: each central bank publishes its meeting schedule in advance.
We hard-code the known 2026 meeting dates and walk backward from today,
trying each predicted URL until we get a 200. More robust than scraping
the calendar HTML (which changes layout across redesigns) and resilient
to mis-typed Month/DD text matches in unrelated parts of the page.

Update the meeting-date lists below at the start of each year.
"""
from __future__ import annotations

import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

DATA_DIR = REPO / "data"
USER_AGENT = "Mozilla/5.0 (nam-hedgefund central-bank fetcher)"
TIMEOUT = 20


# ─── Meeting schedules ──────────────────────────────────────────────────
# Update at the start of each year. Each tuple is the meeting END date
# (which is when the statement is published).

FOMC_MEETINGS_2026 = [
    date(2026, 1, 28),
    date(2026, 3, 18),
    date(2026, 4, 29),
    date(2026, 6, 17),
    date(2026, 7, 29),
    date(2026, 9, 16),
    date(2026, 10, 28),
    date(2026, 12, 9),
]

ECB_MEETINGS_2026 = [
    date(2026, 1, 22),
    date(2026, 3, 5),
    date(2026, 4, 30),
    date(2026, 6, 4),
    date(2026, 7, 23),
    date(2026, 9, 10),
    date(2026, 10, 22),
    date(2026, 12, 17),
]


# ─── HTTP utilities ─────────────────────────────────────────────────────


def _http_get(url: str, allow_404: bool = False) -> str | None:
    """Fetch text from URL. Returns None on 404 if allow_404 (used to
    walk through candidate URLs).

    Forces UTF-8 decoding regardless of what the server claims; both
    Federal Reserve and ECB serve UTF-8 but their headers don't always
    say so, leaving requests to fall back to ISO-8859-1 which mangles
    em-dashes and quotes (the symbols the Fed uses heavily, e.g.
    "3-1/2 percent" with an en-dash that becomes 'â' in latin-1).
    """
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
    if allow_404 and r.status_code == 404:
        return None
    r.raise_for_status()
    r.encoding = "utf-8"
    return r.text


def _strip_html(html: str, content_selectors: list[str] | None = None) -> str:
    """Extract clean text from an HTML page.

    If content_selectors is provided, take only the matching elements
    (e.g. ['#article', '.col-md-8']). Otherwise fall back to extracting
    all <p> and <li> from the body — works but may include nav noise on
    sites that don't use semantic <nav>/<header> tags.
    """
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()

    container = None
    if content_selectors:
        # Find the first selector that yields a substantive container.
        # Some pages have multiple matching elements where the first is
        # a header / sidebar. Prefer the largest match across selectors.
        candidates = []
        for sel in content_selectors:
            for found in soup.select(sel):
                text_len = len(found.get_text(" ", strip=True))
                if text_len >= 500:
                    candidates.append((text_len, found))
        if candidates:
            candidates.sort(key=lambda t: t[0], reverse=True)
            container = candidates[0][1]

    target = container or soup
    paragraphs: list[str] = []
    for p in target.find_all(["p", "li"]):
        text = p.get_text(" ", strip=True)
        if not text:
            continue
        # Skip obvious nav/footer cruft if no container match found
        if not container:
            lc = text.lower()
            if any(skip in lc for skip in (
                "official website of", "share sensitive information",
                "facebook page", "instagram page", "youtube page",
                "linkedin page", "subscribe to rss", "subscribe to email",
                "for media inquiries", "stay connected",
            )):
                continue
        paragraphs.append(text)
    out = "\n\n".join(paragraphs)
    # Normalise: collapse runaway whitespace; convert smart quotes /
    # special hyphens to ASCII so the agent doesn't choke on Unicode that
    # got in via the HTML scrape.
    out = (out.replace("–", "-")     # en dash
              .replace("—", "-")     # em dash
              .replace("‑", "-")     # non-breaking hyphen
              .replace("‘", "'").replace("’", "'")
              .replace("“", '"').replace("”", '"')
              .replace("…", "..."))
    out = re.sub(r"[ \t]+", " ", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


def _write_with_header(path: Path, header_lines: list[str], body: str) -> None:
    """Preserve the existing comment-header block (everything before the
    first non-comment line), replace the body."""
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    kept: list[str] = []
    for line in existing.splitlines():
        s = line.strip()
        if s == "" or s.startswith("#"):
            kept.append(line)
        else:
            break
    while kept and kept[-1].strip() == "":
        kept.pop()
    out = "\n".join(kept) + "\n\n" + "\n".join(header_lines) + "\n\n" + body + "\n"
    path.write_text(out, encoding="utf-8")


# ─── FOMC ────────────────────────────────────────────────────────────────


def fetch_fomc(today: date | None = None) -> bool:
    """Walk known 2026 FOMC meeting dates backward; fetch the most
    recent one whose statement URL returns 200."""
    today = today or date.today()
    out_path = DATA_DIR / "fomc_latest.txt"

    past = [d for d in FOMC_MEETINGS_2026 if d <= today]
    past.sort(reverse=True)
    if not past:
        print("FOMC: no past meetings in 2026 schedule yet", file=sys.stderr)
        return False

    for meeting in past:
        url = (f"https://www.federalreserve.gov/newsevents/pressreleases/"
               f"monetary{meeting.strftime('%Y%m%d')}a.htm")
        try:
            html = _http_get(url, allow_404=True)
        except Exception as e:
            print(f"FOMC: error fetching {url}: {e}", file=sys.stderr)
            continue
        if html is None:
            # 404 — try the prior meeting (statement may not be published yet)
            continue
        # Federal Reserve press release pages put the statement inside
        # <div id="article"> or a .col-md-8 column
        body = _strip_html(html, content_selectors=["#article", ".col-md-8", "main"])
        if len(body) < 500:
            print(f"FOMC: {meeting} response too short", file=sys.stderr)
            continue
        header_lines = [
            f"Source: {url}",
            f"Statement date: {meeting.isoformat()}",
            f"Fetched: {today.isoformat()}",
        ]
        _write_with_header(out_path, header_lines, body)
        print(f"FOMC: wrote {len(body):,} chars from {meeting.isoformat()}")
        return True
    print("FOMC: no statement URL returned 200 for any past 2026 meeting", file=sys.stderr)
    return False


# ─── ECB ─────────────────────────────────────────────────────────────────
# ECB statement URLs follow the pattern:
#   /press/pr/date/{YYYY}/html/ecb.mp{YYMMDD}~{8-char hash}.en.html
# The hash is unpredictable so we can't construct the URL deterministically.
# Two-step: fetch the index page, find the link that matches the meeting
# date YYMMDD substring, then fetch it.


_ECB_BASE = "https://www.ecb.europa.eu"
_ECB_RSS = _ECB_BASE + "/rss/press.xml"
# ECB's regular index pages are JS-rendered so we can't scrape them via
# plain HTTP. The RSS feed for press releases exposes the URLs directly
# in machine-readable form — that's what we use.


def _ecb_find_url_for_date(meeting: date) -> str | None:
    """Look in the ECB RSS feed for a press item whose URL embeds the
    meeting's YYMMDD. Prefers the longer "monetary policy statement
    (with Q&A)" version (`ecb.is{YYMMDD}`) over the shorter press
    release (`ecb.mp{YYMMDD}`) since it includes Lagarde's prepared
    remarks — richer input for the ECB-Watcher's language analysis.
    """
    yymmdd = meeting.strftime("%y%m%d")
    try:
        xml = _http_get(_ECB_RSS)
    except Exception as e:
        print(f"ECB RSS fetch failed: {e}", file=sys.stderr)
        return None
    if xml is None:
        return None
    is_pattern = re.compile(rf"/press/press_conference/monetary-policy-statement/{meeting.year}/html/ecb\.is{yymmdd}~[a-f0-9]+\.en\.html")
    mp_pattern = re.compile(rf"/press/pr/date/{meeting.year}/html/ecb\.mp{yymmdd}~[a-f0-9]+\.en\.html")
    # Prefer the "is" (statement with Q&A) over "mp" (press release)
    m = is_pattern.search(xml)
    if m:
        return _ECB_BASE + m.group(0)
    m = mp_pattern.search(xml)
    if m:
        return _ECB_BASE + m.group(0)
    return None


def fetch_ecb(today: date | None = None) -> bool:
    today = today or date.today()
    out_path = DATA_DIR / "ecb_latest.txt"

    past = [d for d in ECB_MEETINGS_2026 if d <= today]
    past.sort(reverse=True)
    if not past:
        print("ECB: no past meetings in 2026 schedule yet", file=sys.stderr)
        return False

    for meeting in past:
        url = _ecb_find_url_for_date(meeting)
        if not url:
            continue  # earlier meeting may not be on the press list anymore
        try:
            html = _http_get(url)
        except Exception as e:
            print(f"ECB: error fetching {url}: {e}", file=sys.stderr)
            continue
        # ECB press releases use specific content containers
        body = _strip_html(html, content_selectors=[
            ".section", ".main-wrapper-page", "main", "article",
        ])
        if len(body) < 500:
            print(f"ECB: {meeting} response too short", file=sys.stderr)
            continue
        header_lines = [
            f"Source: {url}",
            f"Statement date: {meeting.isoformat()}",
            f"Fetched: {today.isoformat()}",
        ]
        _write_with_header(out_path, header_lines, body)
        print(f"ECB: wrote {len(body):,} chars from {meeting.isoformat()}")
        return True
    print("ECB: no statement URL found for any past 2026 meeting", file=sys.stderr)
    return False


# ─── CLI ────────────────────────────────────────────────────────────────


def main(argv: list[str]) -> int:
    do_fomc = "--ecb-only" not in argv
    do_ecb = "--fomc-only" not in argv
    ok = True
    if do_fomc:
        ok = fetch_fomc() and ok
    if do_ecb:
        ok = fetch_ecb() and ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
