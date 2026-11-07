"""Ideal-point estimates for Wiles and Miller, expressed on the DW-NOMINATE scale.

An ideal point is a person's estimated left-right position, inferred from their choices.
DW-NOMINATE is the ideal-point model for roll-call votes; neither Wiles nor Miller has
cast one, so we estimate their ideal points other ways and report them on the
DW-NOMINATE first-dimension scale (-1 liberal ... +1 conservative) so they can be
compared with members of Congress and with Trump:

1. Text scaling: a ridge model trained to predict legislators' DW-NOMINATE dim1 from
   their tweets (congresstweets, 117th + 118th Congress), applied to each person's
   quotes. Calibrated with a "k-text" design: for held-out legislators we draw k tweets,
   average the predictions, and regress the true score on that average. This gives a
   point estimate and prediction interval *for exactly as much text as we have*.
2. Employer bridge: DW-NOMINATE of the legislators/presidents each person worked for.
3. Trump anchor: Voteview's DW-NOMINATE for Trump's presidential positions.

Run:  python -m mvw.ideal_points <congresstweets_data_dir>
Get training data:  git clone --depth 1 --filter=blob:none --sparse \
        https://github.com/alexlitel/congresstweets <dir> && cd <dir> && \
        git sparse-checkout set --no-cone '/data/2021-0[4-6]-*' '/data/2023-0[1-3]-*.json'
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EXT = ROOT / "data" / "external"
RNG = np.random.default_rng(7)

URL = re.compile(r"https?://\S+|www\.\S+")
MENTION = re.compile(r"@\w+")
AMP = re.compile(r"&amp;")

# Employer bridge: principals each person worked for (sources in docs / REPORT).
PRINCIPALS = {
    "miller": [
        ("Rep. Michele Bachmann (press secretary, 2007-09)", "B001256"),
        ("Rep. John Shadegg (press secretary, 2009)", "S000275"),
        ("Sen. Jeff Sessions (press sec. -> comms director, 2009-16)", "S001141"),
        ("President Trump (2016-21, 2025-)", "TRUMP"),
    ],
    "wiles": [
        ("Rep. Jack Kemp (staff assistant, 1979)", "K000086"),
        ("President Reagan (1980 campaign scheduler)", "REAGAN"),
        ("Rick Scott (2010 campaign mgr; Senate score from 2019-)", "S001217"),
        ("Ron DeSantis (2018 campaign chair; House score 2013-18)", "D000621"),
        ("President Trump (2016-21, 2023-26)", "TRUMP"),
    ],
}


def clean(t: str) -> str:
    return re.sub(r"\s+", " ", MENTION.sub(" ", URL.sub(" ", AMP.sub("&", t)))).strip()


def load_voteview() -> pd.DataFrame:
    return pd.read_csv(EXT / "voteview_members_95-119.csv")


def principal_scores(vv: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for person, plist in PRINCIPALS.items():
        for label, key in plist:
            if key in ("TRUMP", "REAGAN"):
                m = vv[(vv.chamber == "President") & vv.bioname.str.startswith(key)]
            else:
                m = vv[vv.bioguide_id == key]
            rows.append({"person": person, "principal": label, "dw_nominate_dim1": float(m.nominate_dim1.iloc[0])})
    return pd.DataFrame(rows)


def load_training(tweets_dir: Path, vv: pd.DataFrame, per_member: int = 250) -> pd.DataFrame:
    handles = pd.read_csv(EXT / "twitter_bioguide.csv")
    h2b = dict(zip(handles.twitter.str.lower(), handles.bioguide_id))
    recs = []
    for f in sorted(Path(tweets_dir).glob("*.json")):
        congress = 117 if f.name.startswith("2021") else 118
        for t in json.loads(f.read_text()):
            b = h2b.get(t.get("screen_name", "").lower())
            txt = t.get("text", "")
            if not b or txt.startswith("RT @"):
                continue
            txt = clean(txt)
            if len(txt.split()) >= 6:
                recs.append((b, congress, txt))
    df = pd.DataFrame(recs, columns=["bioguide_id", "congress", "text"])
    lab = vv[["bioguide_id", "congress", "nominate_dim1", "party_code"]].dropna(subset=["bioguide_id"])
    lab = lab.drop_duplicates(["bioguide_id", "congress"])
    df = df.merge(lab, on=["bioguide_id", "congress"]).dropna(subset=["nominate_dim1"])
    # Balance: cap tweets per legislator so prolific accounts don't dominate.
    df = df.sample(frac=1.0, random_state=1)
    df = df[df.groupby("bioguide_id").cumcount() < per_member]
    return df.reset_index(drop=True)


def make_model():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import make_pipeline
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=5, max_features=150_000, sublinear_tf=True,
                        lowercase=True, strip_accents="unicode"),
        Ridge(alpha=3.0),
    )


def cross_validate(df: pd.DataFrame, ks: list[int], n_draws: int = 40):
    """Out-of-fold predictions by legislator; k-text calibration per k."""
    from sklearn.model_selection import GroupKFold
    oof = np.zeros(len(df))
    for tr, te in GroupKFold(n_splits=5).split(df, groups=df.bioguide_id):
        m = make_model().fit(df.text.iloc[tr], df.nominate_dim1.iloc[tr])
        oof[te] = m.predict(df.text.iloc[te])
    df = df.assign(oof=oof)
    mem = df.groupby("bioguide_id").agg(true=("nominate_dim1", "first"), pred=("oof", "mean"),
                                       party=("party_code", "first"), n=("oof", "size"))
    out = {
        "n_tweets": int(len(df)), "n_legislators": int(len(mem)),
        "tweet_level_r": float(np.corrcoef(df.nominate_dim1, df.oof)[0, 1]),
        "legislator_level_r_all_tweets": float(np.corrcoef(mem.true, mem.pred)[0, 1]),
        "calibration": {},
    }
    groups = {b: g.oof.to_numpy() for b, g in df.groupby("bioguide_id")}
    truth = mem.true.to_dict()
    for k in ks:
        xs, ys = [], []
        for b, preds in groups.items():
            if len(preds) < k:
                continue
            for _ in range(n_draws):
                xs.append(RNG.choice(preds, k, replace=False).mean()); ys.append(truth[b])
        xs, ys = np.array(xs), np.array(ys)
        slope, intercept = np.polyfit(xs, ys, 1)
        resid = ys - (intercept + slope * xs)
        # How often does a k-text sample put a legislator on the correct side of 0?
        side = np.mean(np.sign(intercept + slope * xs) == np.sign(ys))
        out["calibration"][k] = {"intercept": float(intercept), "slope": float(slope),
                                 "resid_sd": float(resid.std()), "r": float(np.corrcoef(xs, ys)[0, 1]),
                                 "correct_party_side": float(side)}
    return out, mem


def score_people(model, texts: dict[str, list[str]], calib: dict, n_boot: int = 2000):
    res = {}
    for name, tx in texts.items():
        preds = model.predict([clean(t) for t in tx])
        k = len(tx)
        c = calib[k]
        point = c["intercept"] + c["slope"] * preds.mean()
        boots = [c["intercept"] + c["slope"] * RNG.choice(preds, k).mean() for _ in range(n_boot)]
        res[name] = {"n_texts": k, "raw_mean": float(preds.mean()), "estimate": float(point),
                     "pi95": [float(point - 1.96 * c["resid_sd"]), float(point + 1.96 * c["resid_sd"])],
                     "bootstrap95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]}
    return res


def run(tweets_dir: str) -> dict:
    sys.path.insert(0, str(ROOT / "src"))
    from mvw.analysis import CONTENT_STATUSES, load

    vv = load_voteview()
    utt, _ = load()
    usable = utt[~utt.low_confidence & utt.quote_status.isin(CONTENT_STATUSES)]
    dep = pd.read_json(ROOT / "data" / "miller_deposition_2022.jsonl", lines=True)
    texts = {
        "wiles_all": usable[usable.speaker == "wiles"].text.tolist(),
        "miller_all": usable[usable.speaker == "miller"].text.tolist(),
        "wiles_excl_vanity_fair": usable[(usable.speaker == "wiles") & ~usable.vanity_fair].text.tolist(),
        "miller_deposition_2022": dep.text.tolist(),
    }
    df = load_training(Path(tweets_dir), vv)
    cv, mem = cross_validate(df, sorted({len(v) for k, v in texts.items() if k != "miller_deposition_2022"}))
    # The deposition has more texts than most legislators have tweets; calibrate it at k=200.
    texts["miller_deposition_2022"] = texts["miller_deposition_2022"]
    cv_dep, _ = cross_validate(df, [200], n_draws=20)
    cv["calibration"][200] = cv_dep["calibration"][200]
    model = make_model().fit(df.text, df.nominate_dim1)
    calib = cv["calibration"]
    dep_sample = list(RNG.choice(texts.pop("miller_deposition_2022"), 200, replace=False))
    scores = score_people(model, texts, calib)
    scores.update(score_people(model, {"miller_deposition_2022 (200 answers)": dep_sample}, calib))

    # Most partisan n-grams learned by the model (for face validity).
    vec, ridge = model.named_steps["tfidfvectorizer"], model.named_steps["ridge"]
    vocab = np.array(vec.get_feature_names_out())
    order = np.argsort(ridge.coef_)
    terms = {"most_left": vocab[order[:25]].tolist(), "most_right": vocab[order[-25:]][::-1].tolist()}

    # Per-quote predictions (raw model scale) to show which texts pull left or right.
    per_quote = []
    for spk in ("wiles", "miller"):
        sub = usable[usable.speaker == spk]
        for (_, r), p in zip(sub.iterrows(), model.predict([clean(t) for t in sub.text])):
            per_quote.append({"speaker": spk, "id": r["id"], "text": r["text"], "raw_pred": float(p)})
    pd.DataFrame(per_quote).sort_values("raw_pred").to_csv(ROOT / "reports" / "ideal_points_per_quote.csv", index=False)

    party_means = vv[(vv.congress == 118) & vv.party_code.isin([100, 200])].groupby("party_code").nominate_dim1.agg(["mean", "std"])
    out = {
        "validation": cv, "scores": scores, "model_terms": terms,
        "principals": principal_scores(vv).to_dict(orient="records"),
        "reference": {"trump_president": float(vv[(vv.chamber == "President") & vv.bioname.str.startswith("TRUMP")].nominate_dim1.iloc[0]),
                      "house_senate_R_mean_118": float(party_means.loc[200, "mean"]),
                      "house_senate_D_mean_118": float(party_means.loc[100, "mean"])},
    }
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "ideal_points.json").write_text(json.dumps(out, indent=2))
    mem.to_csv(ROOT / "reports" / "ideal_points_validation.csv")
    return out


if __name__ == "__main__":
    r = run(sys.argv[1])
    print(json.dumps({k: r[k] for k in ["scores", "principals", "reference"]}, indent=2))
    print(json.dumps({k: v for k, v in r["validation"].items() if k != "calibration"}, indent=2))
    print(json.dumps(r["validation"]["calibration"], indent=2))
