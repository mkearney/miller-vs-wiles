# Press judgment of Trump's chiefs of staff

Write-up: [reports/press-stance.md](../reports/press-stance.md)

## Pipeline

Run from the repo root. Outputs go to `data/press/`.

| Step | Script | Output |
|---|---|---|
| 1 | `01_sitemaps.py` (lists every article in the outlet sitemaps for each tenure) | `candidates.csv` |
| 2 | `02_fetch.py` (downloads article text; ~1 hour) | `candidates_all.csv`, `txt/` cache |
| 3 | `03_build.py` (keeps articles and sentences about each chief, tags the speaker) | `articles.csv`, `sentences.csv` |
| 4 | `04_score.py sentences.csv` (stance model; ~20 min on CPU) | `sentences_scored.csv` |
| 5 | `05_validation_sample.py` (50 masked sentences per chief) | `validation_key.csv`, `coder_sheet.csv` |
| 6 | `06_analyze.py` (validation, estimates, robustness) | `final_results.csv` |

`gdelt_fetch.py` downloads the GDELT tone series used in the write-up's tone comparison (`gdelt_tone_weekly.csv`).

The sitemap and article caches (`sm/`, `txt/`) are not committed, because they hold full article text.

```bash
pip install pandas numpy trafilatura transformers torch sentencepiece
```

## Second coder: instructions

Open `data/press/coder_sheet.csv`. Each row is one sentence from a news article, with the chief of staff's name replaced by `[CHIEF]`. In the `label` column, enter:

- **1** if the sentence portrays [CHIEF] favorably: praise, success, competence, strong standing, defended by others
- **-1** if it portrays [CHIEF] unfavorably: criticism, failure, scandal, weak or slipping standing, attacked or mocked, false claims
- **0** if it is neutral: logistics, schedule, plain facts, or the sentence only reports what [CHIEF] said

Judge the sentence on its own, not what you know about the person. If it's mixed, choose the side that dominates. If it's truly balanced, choose 0. It takes about an hour.

Save the file as `data/press/validation_labels_human.csv`, with columns `id,label`. Agreement with `validation_labels_claude.csv` can then be computed with Cohen's kappa. Above 0.6 is good agreement.
