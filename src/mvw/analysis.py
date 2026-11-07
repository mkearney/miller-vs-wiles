"""Comparative analysis of Wiles vs. Miller public communication.

Run:  python -m mvw.analysis   (from src/, or via run.py at repo root)
Writes: reports/results.json and reports/figures/*.png
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from .lexicons import LEXICONS, PRONOUNS, count_phrases, tokenize

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = ROOT / "reports"
SPEAKERS = ["wiles", "miller"]
RNG = np.random.default_rng(20261107)

# Analysis sets. "style" needs complete sentences; "content" tolerates fragments.
STYLE_STATUSES = {"full", "stitched"}
CONTENT_STATUSES = {"full", "stitched", "fragment", "paraphrase"}

STOP = set("""a an the and or but of to in on for with at by from as is are was were be been
it its this that these those there their they them he him his she her we our us you your i me my
not no so if then than too very can will would should could do does did have has had just also
into over under up down out about after before because while what which who whom whose how when
where why all any each both more most other some such only own same s t don now""".split())


# ----------------------------------------------------------------------------- data

def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    utt = pd.read_json(DATA / "utterances.jsonl", lines=True, dtype={"date": str}, convert_dates=False)
    per = pd.read_json(DATA / "perceptions.jsonl", lines=True, dtype={"date": str}, convert_dates=False)
    utt["notes"] = utt.get("notes", pd.Series(dtype=str)).fillna("")
    utt["low_confidence"] = utt["notes"].str.contains("low confidence|sensitivity", case=False)
    utt["vanity_fair"] = utt["venue"].str.contains("Vanity Fair", case=False)
    utt["tokens"] = utt["text"].map(tokenize)
    utt["n_tokens"] = utt["tokens"].map(len)
    return utt, per


# ------------------------------------------------------------------------- features

def featurize(df: pd.DataFrame) -> pd.DataFrame:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    sia = SentimentIntensityAnalyzer()
    f = pd.DataFrame(index=df.index)
    for cat, words in LEXICONS.items():
        f[f"lex_{cat}"] = df["text"].map(lambda t, w=words: count_phrases(t, w))
    for p, words in PRONOUNS.items():
        f[f"pro_{p}"] = df["tokens"].map(lambda toks, w=set(words): sum(t in w for t in toks))
    f["n_tokens"] = df["n_tokens"]
    f["exclaim"] = df["text"].str.count("!")
    f["question"] = df["text"].str.count(r"\?")
    f["negation"] = df["tokens"].map(lambda t: sum(x in {"not", "no", "never", "nothing", "nobody", "none", "cannot"} or x.endswith("n't") for x in t))
    f["vader"] = df["text"].map(lambda t: sia.polarity_scores(t)["compound"])
    f["sentences"] = df["text"].map(lambda t: max(1, sum(t.count(c) for c in ".!?")))
    return f


def rate_per_100(f: pd.DataFrame, col: str, idx) -> float:
    toks = f.loc[idx, "n_tokens"].sum()
    return 100 * f.loc[idx, col].sum() / toks if toks else float("nan")


def compare_rates(df, f, cols, mask, n_boot=4000, n_perm=4000):
    """Pooled rate per 100 tokens per speaker, bootstrap CI and permutation p-value."""
    rows = []
    sub = df[mask]
    w_idx = sub.index[sub.speaker == "wiles"].to_numpy()
    m_idx = sub.index[sub.speaker == "miller"].to_numpy()
    all_idx = np.concatenate([w_idx, m_idx])
    for col in cols:
        w, m = rate_per_100(f, col, w_idx), rate_per_100(f, col, m_idx)
        boots_w, boots_m, diffs = [], [], []
        for _ in range(n_boot):
            bw = RNG.choice(w_idx, len(w_idx)); bm = RNG.choice(m_idx, len(m_idx))
            rw, rm = rate_per_100(f, col, bw), rate_per_100(f, col, bm)
            boots_w.append(rw); boots_m.append(rm); diffs.append(rm - rw)
        obs = m - w
        perm = 0
        for _ in range(n_perm):
            sh = RNG.permutation(all_idx)
            pw, pm = sh[: len(w_idx)], sh[len(w_idx):]
            if abs(rate_per_100(f, col, pm) - rate_per_100(f, col, pw)) >= abs(obs) - 1e-12:
                perm += 1
        rows.append({
            "feature": col,
            "wiles": w, "wiles_lo": np.nanpercentile(boots_w, 2.5), "wiles_hi": np.nanpercentile(boots_w, 97.5),
            "miller": m, "miller_lo": np.nanpercentile(boots_m, 2.5), "miller_hi": np.nanpercentile(boots_m, 97.5),
            "diff_m_minus_w": obs,
            "diff_lo": np.nanpercentile(diffs, 2.5), "diff_hi": np.nanpercentile(diffs, 97.5),
            "p_perm": (perm + 1) / (n_perm + 1),
            "n_wiles": len(w_idx), "n_miller": len(m_idx),
        })
    out = pd.DataFrame(rows)
    out["q_bh"] = bh(out["p_perm"].to_numpy())
    return out


def bh(p: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg FDR adjustment."""
    n = len(p); order = np.argsort(p); ranked = p[order] * n / (np.arange(n) + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n); out[order] = np.minimum(q, 1)
    return out


# ---------------------------------------------------------------- distinctive words

def fightin_words(df: pd.DataFrame, mask, alpha0: float = 100.0, top: int = 12):
    """Monroe, Colaresi & Quinn (2008) log-odds ratio with informative Dirichlet prior."""
    sub = df[mask]
    cw = Counter(t for toks in sub[sub.speaker == "wiles"].tokens for t in toks if t not in STOP)
    cm = Counter(t for toks in sub[sub.speaker == "miller"].tokens for t in toks if t not in STOP)
    vocab = set(cw) | set(cm)
    tot = cw + cm
    a = {w: alpha0 * tot[w] / sum(tot.values()) for w in vocab}
    nw, nm, a0 = sum(cw.values()), sum(cm.values()), sum(a.values())
    rows = []
    for w in vocab:
        lw = math.log((cw[w] + a[w]) / (nw + a0 - cw[w] - a[w]))
        lm = math.log((cm[w] + a[w]) / (nm + a0 - cm[w] - a[w]))
        var = 1 / (cw[w] + a[w]) + 1 / (cm[w] + a[w])
        rows.append({"word": w, "z": (lm - lw) / math.sqrt(var), "n_wiles": cw[w], "n_miller": cm[w]})
    fw = pd.DataFrame(rows).sort_values("z")
    return pd.concat([fw.head(top), fw.tail(top)])


# --------------------------------------------------------------------- separability

def separability(df: pd.DataFrame, mask, n_perm: int = 100):
    """Leave-one-out authorship attribution on char n-grams vs. a label-shuffle null."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import balanced_accuracy_score
    from sklearn.model_selection import LeaveOneOut, cross_val_predict
    from sklearn.pipeline import make_pipeline

    sub = df[mask]
    X, y = sub["text"].to_numpy(), (sub["speaker"] == "miller").astype(int).to_numpy()
    pipe = make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True, min_df=1),
        LogisticRegression(max_iter=2000, class_weight="balanced", C=1.0),
    )
    pred = cross_val_predict(pipe, X, y, cv=LeaveOneOut())
    obs = balanced_accuracy_score(y, pred)
    null = []
    for _ in range(n_perm):
        ys = RNG.permutation(y)
        null.append(balanced_accuracy_score(ys, cross_val_predict(pipe, X, ys, cv=LeaveOneOut())))
    return {"balanced_accuracy": obs, "null_mean": float(np.mean(null)),
            "null_95": float(np.percentile(null, 95)),
            "p_perm": (sum(n >= obs for n in null) + 1) / (n_perm + 1), "n": int(len(y))}


# ---------------------------------------------------------------------- categorical

def shares(df, mask, col):
    sub = df[mask]
    t = pd.crosstab(sub[col], sub["speaker"], normalize="columns").reindex(columns=SPEAKERS).fillna(0)
    return t.sort_values("miller", ascending=False)


def perception_summary(per: pd.DataFrame):
    g = per.groupby("subject")[["warmth", "competence", "dominance"]].agg(["mean", "count"])
    by_align = per.groupby(["subject", "alignment"])[["warmth", "competence", "dominance"]].mean().round(2)
    return g, by_align


# ----------------------------------------------------------------------------- main

def run(make_figures: bool = True) -> dict:
    utt, per = load()
    f = featurize(utt)
    usable = ~utt["low_confidence"] & (utt["quote_status"] != "third_party_report")
    style = usable & utt["quote_status"].isin(STYLE_STATUSES)
    content = usable & utt["quote_status"].isin(CONTENT_STATUSES)

    lex_cols = [f"lex_{c}" for c in LEXICONS]
    pro_cols = [f"pro_{p}" for p in PRONOUNS]
    style_cols = pro_cols + ["exclaim", "question", "negation"]

    lex = compare_rates(utt, f, lex_cols, content)
    sty = compare_rates(utt, f, style_cols, style)
    # Sensitivity: drop Vanity Fair (one venue dominates Wiles's corpus).
    lex_novf = compare_rates(utt, f, lex_cols, content & ~utt["vanity_fair"], n_boot=1500, n_perm=1500)

    desc = (utt.assign(**f[["n_tokens"]])
            .groupby(["speaker", "channel"]).size().unstack(0).reindex(columns=SPEAKERS).fillna(0).astype(int))
    status = utt.groupby(["speaker", "quote_status"]).size().unstack(0).reindex(columns=SPEAKERS).fillna(0).astype(int)

    style_stats = {}
    for s in SPEAKERS:
        idx = utt.index[style & (utt.speaker == s)]
        style_stats[s] = {
            "n_utterances": int(len(idx)),
            "tokens": int(f.loc[idx, "n_tokens"].sum()),
            "mean_words_per_sentence": float(f.loc[idx, "n_tokens"].sum() / f.loc[idx, "sentences"].sum()),
            "vader_mean": float(f.loc[utt.index[content & (utt.speaker == s)], "vader"].mean()),
        }

    fn = shares(utt, content, "function")
    fn_novf = shares(utt, content & ~utt["vanity_fair"], "function")
    tg = shares(utt, content, "target")
    aud = shares(utt, content, "audience")
    fw = fightin_words(utt, content)
    sep = separability(utt, content)
    pg, pa = perception_summary(per)

    results = {
        "corpus": {"by_channel": desc.to_dict(), "by_quote_status": status.to_dict(),
                   "n_total": int(len(utt)), "n_perceptions": int(len(per)),
                   "date_range": {s: [utt[utt.speaker == s].date.min(), utt[utt.speaker == s].date.max()] for s in SPEAKERS}},
        "style_summary": style_stats,
        "lexicon_rates": lex.round(3).to_dict(orient="records"),
        "lexicon_rates_without_vanity_fair": lex_novf.round(3).to_dict(orient="records"),
        "style_rates": sty.round(3).to_dict(orient="records"),
        "function_shares": fn.round(3).to_dict(),
        "function_shares_without_vanity_fair": fn_novf.round(3).to_dict(),
        "target_shares": tg.round(3).to_dict(),
        "audience_shares": aud.round(3).to_dict(),
        "fightin_words": fw.round(3).to_dict(orient="records"),
        "separability": sep,
        "perception_means": {s: {k: float(pg.loc[s, (k, "mean")]) for k in ["warmth", "competence", "dominance"]} for s in SPEAKERS},
        "perception_by_alignment": {f"{a}|{b}": v for (a, b), v in pa.to_dict(orient="index").items()},
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(results, indent=2, default=str))
    if make_figures:
        from .figures import make_all
        make_all(utt, per, lex, fn, tg, fw, desc)
    return results


if __name__ == "__main__":
    r = run()
    print(json.dumps({k: r[k] for k in ["style_summary", "separability", "perception_means"]}, indent=2, default=str))
