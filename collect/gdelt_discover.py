"""Find candidate articles quoting each person via the GDELT DOC 2.0 API.

For extending the quote dataset. Requires network access to api.gdeltproject.org:

    python collect/gdelt_discover.py --person miller --start 20241101 --end 20261107 > data/raw/miller_gdelt.jsonl

The output is a list of *candidate* URLs. Next steps:
fetch full text with trafilatura → extract attributed quotes with span grounding
→ dedupe with MinHash → verify against primary transcripts → append to data/utterances.jsonl.
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

QUERIES = {
    "miller": '"Stephen Miller" (said OR posted OR told OR wrote)',
    "wiles": '"Susie Wiles" (said OR posted OR told OR wrote)',
}
API = "https://api.gdeltproject.org/api/v2/doc/doc"


def fetch(query: str, start: str, end: str, maxrecords: int = 250) -> list[dict]:
    params = {
        "query": f"{query} sourcelang:english",
        "mode": "ArtList", "format": "json", "maxrecords": maxrecords,
        "startdatetime": f"{start}000000", "enddatetime": f"{end}235959", "sort": "DateDesc",
    }
    url = f"{API}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r).get("articles", [])


def month_windows(start: str, end: str):
    """GDELT caps results per query, so walk the range one month at a time."""
    y, m = int(start[:4]), int(start[4:6])
    while f"{y:04d}{m:02d}" <= end[:6]:
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        yield f"{y:04d}{m:02d}01", min(f"{ny:04d}{nm:02d}01", end)
        y, m = ny, nm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--person", choices=QUERIES, required=True)
    ap.add_argument("--start", default="20241101")
    ap.add_argument("--end", default="20261107")
    a = ap.parse_args()
    seen = set()
    for s, e in month_windows(a.start, a.end):
        for art in fetch(QUERIES[a.person], s, e):
            if art["url"] in seen:
                continue
            seen.add(art["url"])
            print(json.dumps({"person": a.person, "url": art["url"], "title": art.get("title"),
                              "domain": art.get("domain"), "seendate": art.get("seendate")}))
        time.sleep(1)
    print(f"{len(seen)} candidate articles", file=sys.stderr)


if __name__ == "__main__":
    main()
