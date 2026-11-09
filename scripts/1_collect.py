"""Step 1: find and download every article about each chief.

For each outlet, read its public sitemaps (the dated lists of every article it publishes) for each
tenure. Keep articles published during a chief's tenure whose web address names the chief or says
"chief-of-staff". Download their text.

Writes data/candidates.csv. Downloads are cached in cache/, so reruns are fast.
"""
import datetime as dt
import hashlib
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import trafilatura

from config import CACHE, CHIEFS, DATA

SPANS = [("2017-01-20", "2021-01-20"), ("2025-01-20", "2026-11-06")]


def months(start, end):
    d = dt.date.fromisoformat(start).replace(day=1)
    while d <= dt.date.fromisoformat(end):
        yield d
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)


def days(start, end):
    d = dt.date.fromisoformat(start)
    while d <= dt.date.fromisoformat(end):
        yield d
        d += dt.timedelta(days=1)


def sitemap_jobs():
    """(outlet, sitemap URL, the date or month the sitemap covers)."""
    for s, e in SPANS:
        for m in months(s, e):
            yield "cnn", f"https://www.cnn.com/sitemap/article/politics/{m.year}/{m.month:02d}.xml", m.strftime("%Y-%m")
            yield "nbc", f"https://www.nbcnews.com/sitemap/nbcnews/sitemap-{m.year}-{m.month:02d}-article.xml", m.strftime("%Y-%m")
        for d in days(s, e):
            yield "wex", f"https://www.washingtonexaminer.com/sitemap.xml?yyyy={d.year}&mm={d.month:02d}&dd={d.day:02d}", str(d)


def cached(url, folder):
    return CACHE / folder / hashlib.md5(url.encode()).hexdigest()


def read_sitemap(job):
    outlet, url, period = job
    path = cached(url, "sitemaps")
    if not path.exists() or path.stat().st_size < 50:
        path.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["curl", "-sSL", "-m", "60", "-A", "Mozilla/5.0 (research)", url], capture_output=True, text=True)
        path.write_text(r.stdout)
    rows = []
    for block in re.findall(r"<url>(.*?)</url>", path.read_text(), re.S):
        loc = re.search(r"<loc>([^<]*)</loc>", block)
        lastmod = re.search(r"<lastmod>(\d{4}-\d\d-\d\d)", block)
        if loc:
            rows.append(dict(outlet=outlet, url=loc.group(1).strip(), period=period,
                             lastmod=lastmod.group(1) if lastmod else None))
    return rows


def publication_date(r):
    """Date each article by the sitemap it is filed under."""
    if r.outlet == "wex":                       # daily sitemaps
        return r.period
    if r.outlet == "cnn":                       # CNN URLs carry the date; undated pages are evergreen explainers
        m = re.search(r"/(20\d\d)/(\d\d)/(\d\d)/", r.url)
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None
    if r.lastmod and r.lastmod.startswith(r.period):   # NBC: monthly sitemaps with publication timestamps
        return r.lastmod
    return None


def download(url):
    path = cached(url, "articles").with_suffix(".json")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            doc = trafilatura.bare_extraction(trafilatura.fetch_url(url), with_metadata=True) or {}
            get = doc.get if isinstance(doc, dict) else (lambda k: getattr(doc, k, None))
            text, title = get("text"), get("title")
        except Exception:
            text, title = None, None
        path.write_text(json.dumps({"title": title, "text": text}))
    return str(path.relative_to(CACHE.parent))


if __name__ == "__main__":
    jobs = list(sitemap_jobs())
    with ThreadPoolExecutor(10) as ex:
        urls = pd.DataFrame([row for rows in ex.map(read_sitemap, jobs) for row in rows]).drop_duplicates("url")
    urls["date"] = urls.apply(publication_date, axis=1)
    urls = urls.dropna(subset=["date"])
    print(f"{len(jobs)} sitemaps, {len(urls):,} dated articles")

    candidates = []
    for chief, c in CHIEFS.items():
        in_tenure = urls[(urls.date >= c["start"]) & (urls.date <= c["end"])]
        slug = in_tenure.url.str.lower()
        hit = slug.str.contains(c["surname"].lower()) | slug.str.contains("chief-of-staff")
        if c.get("not_url"):
            hit &= ~slug.str.contains(c["not_url"])
        candidates.append(in_tenure[hit].assign(chief=chief))
    cand = pd.concat(candidates)[["chief", "outlet", "url", "date"]]

    with ThreadPoolExecutor(12) as ex:
        paths = dict(zip(cand.url.unique(), ex.map(download, cand.url.unique())))
    cand["cache"] = cand.url.map(paths)
    cand.to_csv(DATA / "candidates.csv", index=False)
    print(cand.groupby(["chief", "outlet"]).size().unstack(fill_value=0))
