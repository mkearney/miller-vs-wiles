# Codebook

Each sentence comes from a news article and mentions one of Trump's chiefs of staff. The name is replaced by **[CHIEF]**. Code how the sentence **portrays that person**.

| Code | Meaning | Examples |
|---|---|---|
| **+1 favorable** | Praise, success, competence, strong standing with the president, defended or admired by others | "[CHIEF] has been seen as a stabilizing force on an erratic presidency." · "Trump praised [CHIEF] as an aide who gets things done." |
| **−1 unfavorable** | Criticism, failure, scandal, false or disputed claims, weak or slipping standing, attacked or mocked by others | "[CHIEF] has eroded morale in the West Wing." · "Officials have long believed it's just a matter of when [CHIEF] would be fired." |
| **0 neutral** | Logistics, schedules, biography, plain facts, or a sentence that only reports what [CHIEF] said or did without judging it | "[CHIEF] tested positive for Covid-19." · "[CHIEF] spoke to Vanity Fair 11 times." |

## Rules

1. **Judge the person, not the news.** A sentence about a grim event is neutral unless it judges [CHIEF].
2. **Others' judgments count.** If a quoted official, lawmaker or rival praises or attacks [CHIEF], code the portrayal: an attack is −1, praise is +1.
3. **Reported speech is neutral.** "[CHIEF] blasted the Democratic Party" reports what [CHIEF] said; code 0 unless the sentence also judges it.
4. **Mixed sentences:** code the side that dominates. If neither does, code 0.
5. **Code the sentence alone.** Ignore anything you know about the person or the moment.
