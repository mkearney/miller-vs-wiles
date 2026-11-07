# miller-vs-wiles

How do **Susie Wiles** and **Stephen Miller** compare as communicators? Trump named Miller to replace Wiles as White House Chief of Staff on Nov 6, 2026 (effective Nov 9).

## Finding: same agenda, different friction

- **Same agenda.** Miller already ran immigration and homeland security policy as deputy chief of staff under Wiles. His hardline views were White House policy before Nov 9 and remain so after. (Standard left–right ideology scores can't tell the two apart, but those scores miss immigration and executive power, the dimensions where Miller stands out.)
- **Different job.** Wiles's public words point inward: managing staff, defending the team, and (on the record) pushing back on Trump. Miller's point outward: attacking opponents and pushing for more power and force.
- **What changes on Nov 9** is the internal friction, not the direction. The policy accelerator now also runs the process.

→ **[Read the report](reports/REPORT.md)**

![headline](reports/figures/headline.png)

## Repo layout

| Path | What |
|---|---|
| `reports/REPORT.md` | Findings, rated by strength of evidence, plus the post–Nov 9 watch list |
| `docs/METHODOLOGY.md` | Full design: corpus layers, sources, measures, inference, ethics, limits |
| `docs/CODEBOOK.md` | Coding rules for function, target, stance (brake/accelerator) and perception |
| `data/utterances.jsonl` | 99 attributed quotes with channel, audience, quote status, codes and source URL |
| `data/perceptions.jsonl` | 43 descriptions of them by others, coded for warmth, competence and dominance |
| `data/miller_deposition_2022.jsonl` | 450 answers from Miller's Jan. 6 Committee deposition (register check) |
| `data/external/` | Voteview scores (95th–119th Congress) and legislator Twitter handles |
| `src/mvw/analysis.py` | Features, headline indicators, bootstrap/permutation tests with FDR, figures |
| `src/mvw/ideal_points.py` | Ideal points: text scaling on congressional tweets, plus employer bridge |
| `collect/` | WTFJHT quote extractor, deposition parser, GDELT discovery script |

## Run

```bash
pip install pandas numpy scipy scikit-learn vaderSentiment matplotlib pyyaml pytest
# Ideal-point text model (needs congressional tweets; ~1 min)
git clone --depth 1 --filter=blob:none --sparse https://github.com/alexlitel/congresstweets /tmp/ct
(cd /tmp/ct && git sparse-checkout set --no-cone '/data/2021-0[4-6]-*' '/data/2023-0[1-3]-*.json')
cd src && python -m mvw.ideal_points /tmp/ct/data && cd ..
python run.py   # ~3 min; writes reports/results.json and figures
pytest -q
```

## Caveats

The quote sample is small and press-filtered, and Wiles is genuinely low-output. Each quote has a source URL but should be checked against the original. One AI coder did all the coding. The build session couldn't reach news sites or archives directly, so sources came via web search and GitHub mirrors. Details are in the report's limitations section.
