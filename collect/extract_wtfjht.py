"""Extract attributed quotes of Miller / Wiles from WTFJHT daily posts (github.com/mkiser/WTFJHT).

Rule: a sentence must name the person and contain a speech verb; quoted spans of
>= 3 words inside that sentence become candidate quotes. Output is reported speech (L2).
Usage: python -I collect/extract_wtfjht.py <posts_dir> > data/raw/wtfjht_quotes.jsonl
"""
import json
import re
import sys
from pathlib import Path

NAMES = {"miller": re.compile(r"\b(Stephen Miller|Miller)\b"), "wiles": re.compile(r"\b(Susie Wiles|Wiles)\b")}
VERB = re.compile(r"\b(said|says|saying|wrote|writes|posted|posts|told|tells|added|called|declared|argued|claimed|warned|insisted|replied|responded|telling|calling|describ\w+)\b")
QUOTE = re.compile(r"[“\"]([^“”\"]{12,600})[”\"]")
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"])")
OTHER = re.compile(r"\b(Trump|Vance|Leavitt|Noem|Hegseth|Bondi|Rubio|Homan|Musk|Johnson)\b")


def main(posts_dir):
    for f in sorted(Path(posts_dir).glob("*.markdown")):
        date = f.name[:10]
        for para in f.read_text(errors="ignore").split("\n"):
            links = LINK.findall(para)
            text = LINK.sub(r"\1", para)
            for sent in SENT.split(text):
                for spk, rx in NAMES.items():
                    if not rx.search(sent) or not VERB.search(sent):
                        continue
                    # drop sentences where the quote is likely someone else's
                    first_name = rx.search(sent).start()
                    for m in QUOTE.finditer(sent):
                        before = sent[:m.start()]
                        other = OTHER.search(before[first_name:]) if first_name < m.start() else OTHER.search(before)
                        if first_name > m.start() and not VERB.search(sent[m.end():]):
                            continue
                        if other:
                            continue
                        q = m.group(1).strip()
                        if len(q.split()) < 3:
                            continue
                        print(json.dumps({"speaker": spk, "date": date, "text": q, "context": sent.strip()[:400],
                                          "source_urls": [u for _, u in links][:3], "source": f"WTFJHT {f.name}"}))


if __name__ == "__main__":
    main(sys.argv[1])
