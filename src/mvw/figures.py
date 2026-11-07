"""Static figures (PNG) for the report. Two fixed series colors: Wiles=slot 1, Miller=slot 2."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

FIG = Path(__file__).resolve().parents[2] / "reports" / "figures"
COLOR = {"wiles": "#2a78d6", "miller": "#eb6834"}
LABEL = {"wiles": "Wiles", "miller": "Miller"}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"

LEX_NAMES = {
    "lex_threat": "Threat / enemy", "lex_power": "Power / force", "lex_nation": "Nation / belonging",
    "lex_sacred": "Sacred / moral", "lex_certainty": "Certainty", "lex_hedge": "Hedging",
    "lex_management": "Management / process", "lex_affiliation": "Affiliation / warmth",
    "lex_evaluative": "Character evaluation",
}


def _style(ax, title, xlabel=None):
    ax.set_facecolor(SURF)
    ax.set_title(title, loc="left", fontsize=12, color=INK, pad=12, fontweight="bold")
    if xlabel:
        ax.set_xlabel(xlabel, color=INK2, fontsize=9)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9, length=0)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _legend(ax):
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2, loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2, borderaxespad=0.2)


def _save(fig, name):
    fig.patch.set_facecolor(SURF)
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=200)
    plt.close(fig)


def lexicon_dotplot(lex):
    d = lex.copy()
    d["name"] = d.feature.map(LEX_NAMES)
    d = d.sort_values("diff_m_minus_w")
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    for s, off in [("wiles", 0.14), ("miller", -0.14)]:
        ax.hlines(y + off, d[f"{s}_lo"], d[f"{s}_hi"], color=COLOR[s], linewidth=2, alpha=0.55)
        ax.scatter(d[s], y + off, s=48, color=COLOR[s], edgecolor=SURF, linewidth=2, zorder=3, label=LABEL[s])
    labels = [f"{n}{'  *' if q < 0.05 else ''}" for n, q in zip(d.name, d.q_bh)]
    ax.set_yticks(y, labels)
    _style(ax, "Rhetorical vocabulary, hits per 100 words", "rate per 100 words (95% bootstrap CI)   * = FDR q < 0.05")
    _legend(ax)
    _save(fig, "lexicon_rates.png")


def grouped_share(tab, name, title):
    t = tab.copy()
    t = t.loc[(t.max(axis=1) > 0)].sort_values("miller")
    y = np.arange(len(t))
    fig, ax = plt.subplots(figsize=(7.5, 0.42 * len(t) + 1.4))
    h = 0.36
    for s, off in [("wiles", h / 2 + 0.02), ("miller", -h / 2 - 0.02)]:
        ax.barh(y + off, t[s] * 100, height=h, color=COLOR[s], label=LABEL[s])
    ax.set_yticks(y, [i.title() for i in t.index])
    _style(ax, title, "% of each speaker's quotes")
    _legend(ax)
    _save(fig, name)


def fightin(fw):
    d = fw.sort_values("z")
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(7.5, 6.2))
    colors = [COLOR["miller"] if z > 0 else COLOR["wiles"] for z in d.z]
    ax.barh(y, d.z, color=colors, height=0.7)
    ax.set_yticks(y, d.word)
    ax.axvline(0, color=INK2, linewidth=0.8)
    _style(ax, "Most distinctive words (log-odds, informative prior)", "z-score   ← more Wiles   |   more Miller →")
    _save(fig, "distinctive_words.png")


def perception(per):
    fig, ax = plt.subplots(figsize=(6.2, 5.4))
    jitter = np.random.default_rng(1)
    for s in ["wiles", "miller"]:
        p = per[per.subject == s]
        ax.scatter(p.warmth + jitter.uniform(-.18, .18, len(p)), p.competence + jitter.uniform(-.18, .18, len(p)),
                   s=34, color=COLOR[s], alpha=0.45, edgecolor="none")
        ax.scatter(p.warmth.mean(), p.competence.mean(), s=180, color=COLOR[s], edgecolor=SURF, linewidth=2.5,
                   zorder=4, label=f"{LABEL[s]} (mean)")
    ax.axhline(0, color=GRID); ax.axvline(0, color=GRID)
    ax.set_xlim(-1.4, 1.4); ax.set_ylim(-1.4, 1.4)
    ax.set_xticks([-1, 0, 1], ["cold", "", "warm"]); ax.set_yticks([-1, 0, 1], ["incompetent", "", "competent"])
    _style(ax, "How others describe them (stereotype content model)")
    ax.grid(False)
    ax.legend(frameon=False, fontsize=9, labelcolor=INK2, loc="lower left")
    _save(fig, "perception_scm.png")


def corpus(desc):
    t = desc.copy()
    t.index = [i.replace("_", " ") for i in t.index]
    t = t.sort_values("miller")
    y = np.arange(len(t)); h = 0.36
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    for s, off in [("wiles", h / 2 + 0.02), ("miller", -h / 2 - 0.02)]:
        ax.barh(y + off, t[s], height=h, color=COLOR[s], label=LABEL[s])
    ax.set_yticks(y, t.index)
    _style(ax, "What the corpus is made of", "number of quotes")
    _legend(ax)
    _save(fig, "corpus_channels.png")


def make_all(utt, per, lex, fn, tg, fw, desc, headline=None):
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = "DejaVu Sans"
    lexicon_dotplot(lex)
    grouped_share(fn, "functions.png", "What each quote is doing (rhetorical function)")
    grouped_share(tg, "targets.png", "Who each quote is aimed at")
    fightin(fw)
    perception(per)
    corpus(desc)
    ideal_point_chart()
    if headline is not None:
        headline_chart(headline)


def ideal_point_chart(path=None):
    """Ideal-point estimates on the DW-NOMINATE scale, with reference lines."""
    import json
    p = Path(path or FIG.parent / "ideal_points.json")
    if not p.exists():
        return
    r = json.loads(p.read_text())
    s, ref = r["scores"], r["reference"]
    pr = {k: [x["dw_nominate_dim1"] for x in r["principals"] if x["person"] == k] for k in ("wiles", "miller")}
    rows = [  # (label, person, point, lo, hi)
        ("Employer bridge (preferred)\nmean of bosses, range", "wiles", float(np.mean(pr["wiles"])), min(pr["wiles"]), max(pr["wiles"])),
        ("Employer bridge (preferred)\nmean of bosses, range", "miller", float(np.mean(pr["miller"])), min(pr["miller"]), max(pr["miller"])),
        ("Text scaling (lower bound)\nall quotes", "wiles", s["wiles_all"]["estimate"], *s["wiles_all"]["pi95"]),
        ("Text scaling (lower bound)\nall quotes", "miller", s["miller_all"]["estimate"], *s["miller_all"]["pi95"]),
        ("Text scaling\nWiles w/o Vanity Fair;\nMiller deposition", "wiles", s["wiles_excl_vanity_fair"]["estimate"], *s["wiles_excl_vanity_fair"]["pi95"]),
        ("Text scaling\nWiles w/o Vanity Fair;\nMiller deposition", "miller", s["miller_deposition_2022 (200 answers)"]["estimate"], *s["miller_deposition_2022 (200 answers)"]["pi95"]),
    ]
    labels = list(dict.fromkeys(r_[0] for r_ in rows))
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for i, lab in enumerate(labels[::-1]):
        for (l, who, pt, lo, hi) in rows:
            if l != lab:
                continue
            y = i + (0.13 if who == "wiles" else -0.13)
            ax.hlines(y, lo, hi, color=COLOR[who], linewidth=2, alpha=0.55)
            ax.scatter(pt, y, s=52, color=COLOR[who], edgecolor=SURF, linewidth=2, zorder=3,
                       label=LABEL[who] if i == 0 else None)
    for x, name, ha in [(ref["house_senate_D_mean_118"], "avg Democrat", "center"), (ref["trump_president"], "Trump ", "right"),
                        (ref["house_senate_R_mean_118"], " avg Republican", "left")]:
        ax.axvline(x, color=INK2, linewidth=0.8, linestyle=(0, (3, 3)))
        ax.text(x, len(labels) - 0.45, name, color=INK2, fontsize=8, ha=ha)
    ax.set_yticks(range(len(labels)), labels[::-1])
    ax.set_xlim(-0.6, 1.0)
    ax.set_ylim(-0.6, len(labels) - 0.2)
    _style(ax, "Left–right position (ideal points, DW-NOMINATE scale)", "← liberal      conservative →   (bars: 95% prediction interval / range)")
    ax.legend(frameon=True, facecolor=SURF, edgecolor=SURF, framealpha=1, fontsize=9, labelcolor=INK2, loc="lower left")
    _save(fig, "ideal_points.png")


def headline_chart(h):
    """The one-glance comparison: share of quotes meeting each indicator, Wilson 95% CIs."""
    d = h.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(d)); off = 0.17
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    for s, o in [("wiles", off), ("miller", -off)]:
        ax.barh(y + o, d[s] * 100, height=0.3, color=COLOR[s], label=LABEL[s])
        ax.hlines(y + o, d[f"{s}_lo"] * 100, d[f"{s}_hi"] * 100, color=INK2, linewidth=1)
        for yi, v, hi in zip(y + o, d[s] * 100, d[f"{s}_hi"] * 100):
            ax.text(max(v, hi) + 1.2, yi, f"{v:.0f}%", va="center", ha="left", fontsize=8, color=INK2)
    ax.set_yticks(y, d.indicator)
    ax.set_xlim(0, 105)
    _style(ax, "Same agenda, different job", "% of each speaker's quotes (lines: 95% CI)")
    _legend(ax)
    _save(fig, "headline.png")
