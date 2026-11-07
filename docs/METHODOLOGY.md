# Methodology

## Question

Miller's policy agenda was already White House policy before he became chief of staff, so what does the change at the top of the staff actually change? We compare how Wiles and Miller use their public voices: what they talk about, who they target, and whether they push the president's agenda forward or put limits on it.

## Data

**Quotes** (`data/utterances.jsonl`): 99 attributed public statements, 55 from Wiles and 44 from Miller, mostly February 2024 to November 2026. Sources:
- News coverage found through targeted web searches.
- *What The F\*\*\* Just Happened Today* (WTFJHT), a daily news digest that quotes coverage verbatim with links. Candidates were pulled with `collect/extract_wtfjht.py`, then reviewed by hand.

Each record has the date, venue, channel (TV, social post, speech, print interview, memo), the source link, and a **quote status**:
- *full*: a complete sentence.
- *fragment*: a short quoted phrase.
- *paraphrase*: the reporter's wording.
- *third-party report*: attributed through anonymous sources.

Third-party reports, and one quote whose wording conflicts across sources, are excluded from the analysis. That leaves 53 usable Wiles quotes and 41 usable Miller quotes.

**Descriptions by others** (`data/perceptions.jsonl`): 43 characterizations of the two by allies, critics and news reporters.

**Miller's deposition** (`data/miller_deposition_2022.jsonl`): 450 answers from his April 2022 testimony to the House Jan. 6 Committee, parsed from OCR'd transcripts with `collect/parse_deposition.py`. It is used only to compare his public voice with his testimony.

## Coding

Each quote is coded for **function** (attack, assert power, rally supporters, announce policy, defend, show loyalty, evaluate colleagues candidly, manage, strategize, personal), **target** (opposition, immigrants, courts, foreign governments, media, Trump, colleagues, staff, public, self), and **stance**:
- **accelerator**: pushes for more executive power, force or enforcement, or for escalation against opponents.
- **brake**: signals limits, disagreement, doubt or de-escalation about the president or a policy.
- **neutral**: neither.

Rules and examples are in `CODEBOOK.md`. One coder (an AI model) applied the codes; there is no second-coder reliability check yet.

## Measures and statistics

- **Headline indicators:** each person's share of usable quotes meeting a condition (e.g. stance = accelerator), with Wilson 95% confidence intervals.
- **Vocabulary:** hits per 100 words from small, transparent word lists (threat, power, management, hedging, and others) plus pronoun rates. Speakers are compared with bootstrap confidence intervals and permutation tests, with a Benjamini–Hochberg false-discovery-rate correction. Some list terms were chosen after reading the quotes, which inflates these differences; treat them as descriptive.
- **Robustness:** every comparison is rerun without the Vanity Fair interviews, which supply 27 of Wiles's 55 quotes.
- **Perceptions:** each description is scored −1/0/+1 for warmth, competence and dominance, and summarized by the describer's alignment (ally, critic, neutral).
- **Ideology scores** (`src/mvw/ideal_points.py`): estimated positions on the congressional left–right scale (DW-NOMINATE), using two methods:
  - **from their bosses:** the Voteview scores of the politicians each person worked for;
  - **from their words:** a ridge regression trained on 81,365 congressional tweets, validated on held-out legislators (r = 0.94 from 26–53 tweets each).

  As explained in the supporting analyses, this scale misses the issues where the two differ, so the scores play no part in the main finding.

## Limitations

- **Small, press-filtered sample.** The quotes are what journalists chose to report, which favors Miller's most combative lines and Wiles's most candid ones.
- **Wiles's brake signals rest mainly on one source**, her December 2025 Vanity Fair interviews, plus third-party reporting.
- **Wording is unverified.** Most quotes were gathered from news summaries and digests rather than primary transcripts, so check wording against the linked source before citing.
- **One coder,** with no reliability check.

## Extending this

- **Primary sources:** full TV transcripts, complete X timelines and speech texts would replace press-selected quotes, and would let us measure how much the press favors extreme lines.
- **A second human coder** for the stance and function codes, with Krippendorff's α reported.
- **After November 9:** track the indicators listed at the end of the report (pushback signals, visibility, register, pace of executive action) for Miller as chief of staff.
