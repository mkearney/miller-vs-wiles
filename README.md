# miller-vs-wiles

Comparing the public communication of **Susie Wiles** and **Stephen Miller**. Trump named Miller to replace Wiles as White House Chief of Staff on Nov 6, 2026 (effective Nov 9).

**Headline (v2):** Both sit in the same place on the DW-NOMINATE left–right scale (≈ +0.55, mainstream Republican; neither has roll-call votes, so this is estimated). Where they differ is communication role: Wiles's public words point *inward*, at Trump, staff and process, while Miller's point *outward*, at opponents, immigrants, courts and foreign states. Under oath, Miller sounds much more like Wiles, so part of the gap is the register he uses on public stages.
→ [reports/REPORT.md](reports/REPORT.md)

## Repo layout

| Path | What |
|---|---|
| `docs/METHODOLOGY.md` | The full analysis design: corpus layers, sources, pipeline, measures, inference, ethics, v1 limits |
| `docs/CODEBOOK.md` | Function / target / perception coding rules |
| `data/utterances.jsonl` | 99 attributed quotes with channel, audience, quote status, codes, source URL |
| `data/perceptions.jsonl` | 43 third-party descriptors coded for warmth / competence / dominance |
| `data/miller_deposition_2022.jsonl` | 450 answers from Miller's Jan. 6 Committee deposition (register check) |
| `data/external/` | Voteview DW-NOMINATE (95th–119th Congress) and legislator Twitter handles |
| `src/mvw/nominate.py` | DW-NOMINATE estimates: text scaling trained on congressional tweets, plus employer bridge |
| `src/mvw/` | Lexicons, features, statistics (bootstrap, permutation, FDR, log-odds, LOO classifier), figures |
| `collect/` | WTFJHT quote extractor, deposition parser, GDELT discovery script |
| `reports/` | `REPORT.md`, `results.json`, figures |

## Run

```bash
pip install pandas numpy scipy scikit-learn vaderSentiment matplotlib pytest
# DW-NOMINATE text model (needs congressional tweets; ~1 min)
git clone --depth 1 --filter=blob:none --sparse https://github.com/alexlitel/congresstweets /tmp/ct
(cd /tmp/ct && git sparse-checkout set --no-cone '/data/2021-0[4-6]-*' '/data/2023-0[1-3]-*.json')
cd src && python -m mvw.nominate /tmp/ct/data && cd ..
python run.py          # ~3 min (permutation tests); writes reports/results.json + figures
pytest -q
```

## Status

v2 adds GitHub-hosted sources (Voteview mirrors, congresstweets, Jan. 6 transcripts, the WTFJHT news digest) because the build session's network blocks news sites and archives directly. Each quote has a source URL but needs checking against the original wording. The full design, including what more network access would unlock, is in `docs/METHODOLOGY.md`.
