# miller-vs-wiles

Comparing the public communication of **Susie Wiles** and **Stephen Miller**. Trump named Miller to replace Wiles as White House Chief of Staff on Nov 6, 2026 (effective Nov 9).

**Headline (v1):** Wiles's public words point *inward*, at Trump, staff and process. Miller's point *outward*, at opponents, immigrants, courts and foreign states. Their sentence-level style is similar. Their functions and targets almost don't overlap.
→ [reports/REPORT.md](reports/REPORT.md)

## Repo layout

| Path | What |
|---|---|
| `docs/METHODOLOGY.md` | The full analysis design: corpus layers, sources, pipeline, measures, inference, ethics, v1 limits |
| `docs/CODEBOOK.md` | Function / target / perception coding rules |
| `data/utterances.jsonl` | 77 attributed quotes with channel, audience, quote status, codes, source URL |
| `data/perceptions.jsonl` | 38 third-party descriptors coded for warmth / competence / dominance |
| `src/mvw/` | Lexicons, features, statistics (bootstrap, permutation, FDR, log-odds, LOO classifier), figures |
| `collect/` | v2 discovery script (GDELT) for scaling the corpus |
| `reports/` | `REPORT.md`, `results.json`, figures |

## Run

```bash
pip install pandas numpy scipy scikit-learn vaderSentiment matplotlib pytest
python run.py          # ~3 min (permutation tests); writes reports/results.json + figures
pytest -q
```

## Status

v1 is a working prototype on a small, press-filtered sample collected through web search, because direct page fetches were blocked in the build sandbox. Each quote has a source URL but needs checking against the original wording. The v2 plan (full transcripts and timelines, dedupe and verification, human-validated coding) is in `docs/METHODOLOGY.md`.
