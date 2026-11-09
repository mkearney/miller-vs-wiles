"""Step 3: draw the random sample of sentences to hand-code (50 per chief).

The chief's name is replaced with [CHIEF] so the coder judges what the sentence says, not who it is
about. Coded sentences live in data/coded_sample.csv. Rerunning this script keeps every coded
sentence that is still in the corpus and tops each chief back up to 50 with new random draws (blank
label). It also writes data/second_coder_sheet.csv, a blank copy for an independent coder.
"""
import re

import pandas as pd

from config import CHIEFS, DATA, SAMPLE_PER_CHIEF

COLS = ["id", "chief", "outlet", "date", "url", "sentence", "masked", "label"]


def mask(chief, sentence):
    c = CHIEFS[chief]
    first, sur = c["name"].split()[0], c["surname"]
    s = re.sub(rf"\b{first}\s+(F\.\s+)?{sur}\b", "[CHIEF]", sentence)
    s = re.sub(rf"\b(Mr\.|Ms\.|Gen\.|General)\s+{sur}\b", "[CHIEF]", s)
    return re.sub(rf"\b{sur}\b", "[CHIEF]", s)


if __name__ == "__main__":
    corpus = pd.read_csv(DATA / "sentences.csv")
    path = DATA / "coded_sample.csv"
    coded = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=COLS)

    in_corpus = set(zip(corpus.chief, corpus.sentence))
    keep = coded[[(c, s) in in_corpus for c, s in zip(coded.chief, coded.sentence)]]
    dropped = len(coded) - len(keep)

    new_rows, next_id = [], int(coded.id.max()) + 1 if len(coded) else 0
    for chief in CHIEFS:
        need = SAMPLE_PER_CHIEF - (keep.chief == chief).sum()
        pool = corpus[(corpus.chief == chief) & ~corpus.sentence.isin(keep.sentence)]
        for r in pool.sample(max(need, 0), random_state=2026).itertuples():
            new_rows.append(dict(id=next_id, chief=chief, outlet=r.outlet, date=r.date, url=r.url,
                                 sentence=r.sentence, masked=mask(chief, r.sentence), label=None))
            next_id += 1

    out = pd.concat([keep, pd.DataFrame(new_rows, columns=COLS)])[COLS].sort_values("id")
    out.to_csv(path, index=False)
    out[["id", "masked"]].rename(columns={"masked": "sentence"}).assign(label="").sample(frac=1, random_state=1) \
        .to_csv(DATA / "second_coder_sheet.csv", index=False)

    print(f"kept {len(keep)} coded sentences, dropped {dropped} no longer in the corpus, added {len(new_rows)} to code")
    for r in out[out.label.isna()].itertuples():
        print(f"  needs a label: id {r.id} ({r.chief}): {r.masked}")
