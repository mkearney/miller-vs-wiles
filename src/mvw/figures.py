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


def make_all(utt, per, lex, fn, tg, fw, desc):
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = "DejaVu Sans"
    lexicon_dotplot(lex)
    grouped_share(fn, "functions.png", "What each quote is doing (rhetorical function)")
    grouped_share(tg, "targets.png", "Who each quote is aimed at")
    fightin(fw)
    perception(per)
    corpus(desc)
