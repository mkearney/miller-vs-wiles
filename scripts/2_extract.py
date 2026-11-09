"""Step 2: keep the articles that are about each chief, and pull out the sentences about them.

An article counts if it names the chief in full and mentions them in at least two sentences.
From each article we keep up to 8 sentences that mention the chief, and drop sentences where the
chief is the one speaking ("Kelly said..."): those report what the chief said, not how the press
judged them.

Writes data/articles.csv and data/sentences.csv.
"""
import json
import re

import pandas as pd

from config import CACHE, CHIEFS, DATA

SPLIT = re.compile(r'(?:(?<=[.!?])|(?<=[.!?]["”]))\s+(?=["“A-Z])')
SPEECH = r"(said|says|told|wrote|added|tweeted|posted|argued|insisted|explained|stated)"


def chief_is_speaking(sentence, c):
    name, sur = c["name"], c["surname"]
    return bool(re.search(rf"({sur}|{name})\s*,?\s*{SPEECH}\b", sentence) or
                re.search(rf"\b(said|says|told|according to)\s+(the\s+)?([\w\s]*chief of staff\s+)?({name}|{sur})\b", sentence))


if __name__ == "__main__":
    cand = pd.read_csv(DATA / "candidates.csv")
    articles, sentences = [], []
    for r in cand.itertuples():
        c = CHIEFS[r.chief]
        doc = json.loads((CACHE.parent / r.cache).read_text())
        text = doc.get("text") or ""
        if not re.search(c["full"], text):
            continue
        mentions = [s.strip() for s in SPLIT.split(text.replace("\n", " "))
                    if c["surname"] in s and 30 < len(s) < 600
                    and not (c.get("not_text") and re.search(c["not_text"], s))]
        if len(mentions) < 2:
            continue
        articles.append(dict(chief=r.chief, outlet=r.outlet, date=r.date, title=doc.get("title"), url=r.url))
        for s in mentions[:8]:
            if not chief_is_speaking(s, c):
                sentences.append(dict(chief=r.chief, outlet=r.outlet, date=r.date, url=r.url, sentence=s))

    articles = pd.DataFrame(articles).drop_duplicates(["chief", "url"])
    sentences = pd.DataFrame(sentences).drop_duplicates(["chief", "sentence"])   # syndicated copies
    articles.to_csv(DATA / "articles.csv", index=False)
    sentences.to_csv(DATA / "sentences.csv", index=False)
    print(pd.DataFrame({"articles": articles.groupby("chief").size(), "sentences": sentences.groupby("chief").size()}))
