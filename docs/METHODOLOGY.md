# Methodology: comparing Susie Wiles and Stephen Miller as communicators

On Nov 6, 2026 Trump announced that Stephen Miller would replace Susie Wiles as
White House Chief of Staff, effective Nov 9. This document lays out how I would
build a rigorous comparison of the two from their public communication. It also
says which parts this repo's v1 implements and which wait for v2.

---

## 1. The core problem: two very different evidence bases

The main fact about this comparison is that **the two corpora are not alike**:

| | Wiles | Miller |
|---|---|---|
| Public volume | Very low. She avoids cameras and posts rarely. | Very high: daily X posts, Fox hits, speeches, briefings |
| Typical channel | Print interviews, rare TV, short X statements, internal memos | Social media, TV, rallies, press gaggles |
| Biggest single source | Vanity Fair (Whipple), 11 recorded interviews, Dec 2025 | No single source dominates |
| Who controls the framing | Mostly journalists, in long-form profiles | Mostly Miller himself |

So a naive "compare all their words" design compares **channels and gatekeepers**,
not people. Every design choice below aims to separate *person* effects from
*channel*, *audience*, *gatekeeper* and *volume* effects.

## 2. Research questions

1. **Voice.** How do they differ in style: pronouns, certainty versus hedging, sentence shape, tone?
2. **Function.** What is each quote *doing*: attacking, asserting power, managing, defending, praising?
3. **Targets.** Who do they talk about: out-groups (opposition, immigrants, courts, foreign states) or insiders (Trump, colleagues, staff)?
4. **Worldview / power posture.** Do they use threat, securitization, sovereignty or sacred framing? How do they talk about the limits of power?
5. **Mediated persona.** How do allies, critics and neutral reporters describe them? (This is the second-hand layer.)
6. **Forecast.** What does the comparison suggest about how the Chief of Staff role will be *communicated* under Miller? Which of these measures can be tracked after Nov 9 to test that?

## 3. Corpus design: four layers, kept separate

| Layer | What it is | Examples | Use |
|---|---|---|---|
| **L1 Own voice** | Words the person verifiably authored or spoke, from the primary record | X posts, full TV transcripts, speeches, memos | All analyses; the gold standard |
| **L2 Reported speech** | Their words as quoted or paraphrased in news coverage | "Wiles said X," headline pull-quotes | Content analysis; lets us measure *quotability bias* |
| **L3 Perception** | What *others* say about them | "Ice Maiden," "true believer," "architect" | Persona analysis (stereotype content model) |
| **L0 Institutional / ghost-written** (optional) | Text they likely shaped but didn't sign | Miller-drafted Trump speeches and EOs, WH statements | Only with explicit attribution-uncertainty weights |

Every record carries `quote_status` (full / fragment / stitched / paraphrase /
third-party report), `channel`, `audience`, `venue`, `date`, `source_url`, and the
annotation fields. The analysis sets **filter on these fields**: style metrics use
complete sentences only, and content metrics tolerate fragments.

## 4. Ideal sources (v2)

- **X/Twitter**: @StephenM and @SusieWiles timelines, via the API or archived snapshots (Wayback, Social Feed Manager).
- **TV and radio transcripts**: CNN transcripts, Internet Archive TV News, Grabien/TVEyes for Fox, C-SPAN.
- **Speeches and remarks**: whitehouse.gov, the American Presidency Project (UCSB), RealClearPolitics video transcripts.
- **Podcasts and video without transcripts**: Whisper ASR plus pyannote diarization, spot-checked by hand.
- **News at scale**: GDELT DOC 2.0 and Media Cloud for discovery; Factiva or LexisNexis for full text.
- **Long-form and books**: Whipple's Vanity Fair series and audio; profiles in The Atlantic, Politico, FT, NYT.
- **Documents**: FOIA releases, court filings, leaked memos, and the 2019 SPLC release of Miller–Breitbart emails. Handle this last one with an explicit ethics review, and keep it as its own layer.

## 5. Pipeline

```
discover → fetch → normalize → dedupe → attribute → verify → enrich → annotate → analyze → report
```

1. **Discover**: GDELT and Media Cloud queries per person, plus a seed list of primary venues.
2. **Fetch and normalize**: trafilatura for articles, the platform API for posts, ASR for audio.
3. **Dedupe**: a single quote appears in hundreds of syndicated stories. Use MinHash/LSH on the quote text and keep one canonical record with a `n_outlets` count. The count is a useful *virality/quotability* feature in its own right.
4. **Attribute**: quote-attribution extraction (LLM with span grounding: the model must return character offsets into the source text, which are then verified) to get `speaker`, `quote`, and `is_direct`.
5. **Verify**: fuzzy-match each L2 quote to an L1 primary record (rapidfuzz, ratio ≥ 90). Unmatched quotes stay L2. Conflicting renderings are kept as variants (example: Miller's "dragon you have awakened" versus "what they have awakened").
6. **Enrich**: outlet lean (AllSides / Ad Fontes), audience type, role period (pre- vs post-inauguration; post-Nov 9 for Miller as CoS).
7. **Annotate**: see §6 and `CODEBOOK.md`.

## 6. Measures

| Construct | v1 (this repo) | v2 (publication grade) |
|---|---|---|
| Stylometry | pronoun rates, sentence length, questions/exclamations, negation | Burrows' Delta on function words; char n-gram attribution |
| Psycholinguistics | transparent mini-lexicons | LIWC-22 (Analytic, Clout, Authentic, Tone) |
| Epistemic stance | hedge vs certainty lexicons | Hyland stance markers; **integrative complexity** (Suedfeld; automated AutoIC) |
| Moral framing | "sacred" lexicon | MFD 2.0 / eMFD |
| Threat & securitization | threat lexicon | supervised classifier trained on the codebook |
| Power motive | power lexicon | Winter running-text motive scoring (LLM-assisted, human-validated) |
| Populism | — | Hawkins holistic grading; Rooduijn & Pauwels dictionary |
| Rhetorical function & target | single-coder codebook (Claude in this session) | LLM coding + 2 human coders on a 20% gold set, Krippendorff's α ≥ 0.7 |
| Issue agenda | targets | Comparative Agendas Project codes; BERTopic |
| Semantic position | — | sentence embeddings; distance to a Trump reference corpus ("who sounds more like the boss") |
| Persona | SCM warmth/competence/dominance, hand-coded | LLM-coded at scale, split by outlet alignment |
| Sentiment | VADER | NRC emotion + transformer sentiment |

## 7. Inference: separating people from confounds

- **Channel and audience**: stratify by channel and report channel-matched contrasts, e.g. social vs social. In v2, fit hierarchical models: `rate ~ speaker + (1|channel) + (1|venue)` with a Poisson/NB offset for token count.
- **Gatekeeper / quotability bias**: for any venue with both a full transcript (L1) and press quotes (L2), estimate how much more extreme the quoted subset is. This tells us how far the *mediated* persona is from the *actual* one.
- **Single-source dominance**: rerun every analysis with the dominant venue left out (v1 drops Vanity Fair for Wiles).
- **Volume asymmetry**: rate per 100 words; bootstrap over utterances. In v2, also downsample Miller to Wiles's size and look at the spread across samples.
- **Multiple comparisons**: permutation tests with Benjamini–Hochberg FDR.
- **Dictionary circularity**: dictionaries must be fixed *before* looking at the corpus. v1's mini-lexicons were partly refined while reading it (see Limitations), so v1 lexicon results count as descriptive only.
- **Time**: interrupted time series on Miller's output around Nov 9, 2026. Does the CoS role pull him toward MANAGE/LOYALTY functions, or does he keep the ATTACK/POWER register?

## 8. Ethics and framing

- Both are senior public officials speaking in public roles. The analysis describes **communication**, not psychology. Following the spirit of the Goldwater rule, it makes no clinical or character diagnoses.
- Second-hand material is always labeled as such and is never mixed into own-voice metrics.
- Pejorative third-party labels ("fascist," "madman") are recorded as *data about perception*, coded by source alignment, and never adopted as findings.

## 9. What v1 actually is

v1 was built in a sandbox where **direct page fetches were blocked**; only a web
search tool worked. So v1 consists of:

- 77 quote records (38 Wiles, 39 Miller) and 38 third-party descriptors, each with a source URL, gathered through ~35 targeted searches;
- the full analysis pipeline (features, permutation/bootstrap stats, FDR, fightin'-words, LOO attribution classifier, SCM persona coding, sensitivity runs);
- figures and a findings report.

**Treat v1 as a working prototype on a small, press-filtered sample.** The code
is built to take the v2 corpus without changes to the analysis layer.

## 10. Limitations of v1 (read before citing anything)

1. **Small n.** About 37 usable quotes per person. Confidence intervals are wide, and only large effects can be detected.
2. **Search-surfaced text.** Quotes came from search-engine summaries of news articles, not the articles themselves. Wording may differ slightly from the original, and every record needs verifying against its `source_url`.
3. **Press selection.** Both corpora are mostly L2: what journalists chose to quote. That favors Miller's most inflammatory lines and Wiles's most candid ones.
4. **Single coder.** Function, target and SCM codes were assigned by one coder (the AI assistant that built this). No reliability was measured.
5. **Lexicons partly fit to the data.** Several terms (e.g. "zealot," "dragon," "trains on the tracks") were added after reading the corpus. That inflates lexicon contrasts. The function/target coding and the classifier are less exposed to this problem.
6. **Asymmetric channels.** Miller has speeches and rallies; Wiles has none. Wiles has long-form print interviews; Miller has none in the sample.
