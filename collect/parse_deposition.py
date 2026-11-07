"""Extract the witness's answers ("A" turns) from a GPO-OCR'd J6 deposition transcript.

Source: github.com/epicfaace/jan6report (OCR of House Select Committee releases).
Usage: python -I collect/parse_deposition.py <transcript.txt> <speaker> <date> <source_url> > out.jsonl
Each output row is one answer, split into sentences, with OCR line numbers and page furniture removed.
"""
import json
import re
import sys

LINE_NO = re.compile(r"^\s*\d{1,2}\s+")
PAGE = re.compile(r"\s+\d{1,3}\s*$")
OTHER = re.compile(r"^(Q\b|Mr\.|Ms\.|Mrs\.|BY|The Reporter|The Witness\.|\[|EXAMINATION|\(Whereupon|Off the record)")


def answers(text):
    cur, mode = [], None
    for raw in text.splitlines():
        line = LINE_NO.sub("", raw).strip()
        if not line or line.isdigit():
            continue
        if re.match(r"^A\b\s*", line):
            if cur and mode == "A":
                yield " ".join(cur)
            cur, mode = [re.sub(r"^A\b\s*", "", line)], "A"
        elif OTHER.match(line):
            if cur and mode == "A":
                yield " ".join(cur)
            cur, mode = [], "other"
        elif mode == "A":
            cur.append(PAGE.sub("", line))
    if cur and mode == "A":
        yield " ".join(cur)


def main(path, speaker, date, url):
    text = open(path, errors="ignore").read()
    n = 0
    for i, a in enumerate(answers(text)):
        a = re.sub(r"\s+", " ", a.replace("--", " -- ")).strip()
        if len(a.split()) < 4:
            continue
        n += 1
        print(json.dumps({"id": f"DEP{n:04d}", "speaker": speaker, "date": date, "text": a,
                          "venue": "House Select Committee (Jan. 6) deposition", "channel": "deposition",
                          "audience": "legal", "quote_status": "full", "source_url": url}))


if __name__ == "__main__":
    main(*sys.argv[1:5])
