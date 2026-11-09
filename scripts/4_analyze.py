"""Step 4: score each chief from the hand-coded sample and draw the chart.

Net judgment = share of sentences favorable minus share unfavorable (-1 to +1).
95% ranges come from resampling the 50 sentences 10,000 times.
If data/second_coder_labels.csv exists (columns id,label), the script also reports how often the two
coders agree.

Writes data/results.csv and figures/press_judgment.png.
"""
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import DATA, FIGURES, LABEL, ORDER

rng = np.random.default_rng(2026)
FIRST_TERM = ["priebus", "kelly", "mulvaney", "meadows"]


def interval(values, stat=np.mean, n=10_000):
    draws = [stat(rng.choice(values, len(values))) for _ in range(n)]
    return np.percentile(draws, [2.5, 97.5])


def cohens_kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    observed = (a == b).mean()
    expected = sum((a == c).mean() * (b == c).mean() for c in np.union1d(a, b))
    return (observed - expected) / (1 - expected)


if __name__ == "__main__":
    coded = pd.read_csv(DATA / "coded_sample.csv")

    rows = []
    for chief in ORDER:
        v = coded[coded.chief == chief].label.to_numpy()
        lo, hi = interval(v)
        rows.append(dict(chief=chief, net=v.mean(), low=lo, high=hi, favorable=(v == 1).mean(),
                         unfavorable=(v == -1).mean(), neutral=(v == 0).mean(), sentences=len(v)))
    res = pd.DataFrame(rows)
    res.round(3).to_csv(DATA / "results.csv", index=False)
    print(res.set_index("chief").round(2).to_string())

    # Wiles compared with the average of the four first-term chiefs
    w = coded[coded.chief == "wiles"].label.to_numpy()
    first = [coded[coded.chief == k].label.to_numpy() for k in FIRST_TERM]
    diff = w.mean() - np.mean([f.mean() for f in first])
    draws = [rng.choice(w, len(w)).mean() - np.mean([rng.choice(f, len(f)).mean() for f in first]) for _ in range(10_000)]
    print(f"\nWiles minus first-term average: {diff:+.2f} (95% range {np.percentile(draws, 2.5):+.2f} to {np.percentile(draws, 97.5):+.2f})")

    second = DATA / "second_coder_labels.csv"
    if second.exists():
        both = coded.merge(pd.read_csv(second), on="id", suffixes=("", "_2"))
        print(f"Second coder: {len(both)} sentences, agreement {100 * (both.label == both.label_2).mean():.0f}%, "
              f"kappa {cohens_kappa(both.label, both.label_2):.2f}")

    # Chart: share unfavorable (left) and favorable (right) for each chief, net score at the end
    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=200)
    y = np.arange(len(ORDER))[::-1]
    ax.barh(y, -100 * res.unfavorable, color="#cf222e", height=0.55, label="Unfavorable")
    ax.barh(y, 100 * res.favorable, color="#0969da", height=0.55, label="Favorable")
    ax.axvline(0, color="#57606a", lw=1)
    for yi, r in zip(y, res.itertuples()):
        net = "0.00" if abs(r.net) < 0.005 else f"{r.net:+.2f}"
        ax.text(100 * r.favorable + 2, yi, f"net {net}", va="center", fontsize=8.5, color="#24292f")
    ax.set_yticks(y, [LABEL[k] for k in ORDER])
    ax.set_xlim(-50, 45)
    ax.set_xticks([-40, -20, 0, 20, 40], ["40%", "20%", "0", "20%", "40%"])
    ax.set_xlabel("Share of sentences about the chief (the rest are neutral)")
    ax.set_title("How the press judged each Trump chief of staff", loc="left", fontweight="bold", pad=12)
    ax.text(-2, len(ORDER) - 0.35, "← Unfavorable", ha="right", fontsize=9, color="#cf222e", fontweight="bold")
    ax.text(2, len(ORDER) - 0.35, "Favorable →", ha="left", fontsize=9, color="#0969da", fontweight="bold")
    ax.set_ylim(-0.6, len(ORDER) - 0.1)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    FIGURES.mkdir(exist_ok=True)
    fig.savefig(FIGURES / "press_judgment.png")
