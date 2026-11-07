"""Theory-driven dictionaries for political-communication features.

Each category is small, transparent and hand-built so every hit can be audited.
They are proxies inspired by established instruments, not replacements for them:

- hedge / certainty: epistemic stance (Hyland 1998; LIWC "tentative"/"certain")
- threat / enemy:     securitization and out-group threat framing (Buzan et al.)
- power / force:      dominance and state-capacity language (Winter 2005 power motive)
- sacred / moral:     moral absolutism and religious register (Moral Foundations: sanctity)
- nation / belonging: nativist in-group boundary language
- management:         organizational/process vocabulary (chief-of-staff as operator)
- affiliation:        warmth, gratitude, relational language (Winter affiliation motive)
- evaluative:         character judgements of named people

Swap in licensed LIWC-22 / MFD 2.0 / NRC dictionaries for publication-grade work.
"""

import re

LEXICONS = {
    "hedge": [
        "i think", "sort of", "kind of", "might", "maybe", "perhaps", "would argue",
        "may", "a little bit", "loose", "probably", "seems",
    ],
    "certainty": [
        "clear", "crystal clear", "always", "never", "nothing", "zero", "of course",
        "absolutely", "only", "every", "will", "cannot", "no idea", "completely",
        "minimum", "not going anywhere",
    ],
    "threat": [
        "insurrection", "invaders", "invasion", "terror", "terrorism", "terrorist",
        "terrorists", "extremist", "violent", "violence", "murder", "assassin",
        "criminals", "crime", "enemy", "enemies", "fifth column", "seditious",
        "attack", "coup", "kill", "hatred", "wickedness",
    ],
    "power": [
        "power", "force", "strength", "authority", "plenary", "sovereignty",
        "dismantle", "destroy", "disrupt", "deport", "arrests", "military",
        "armada", "fleet", "embargo", "permission", "terms and conditions",
        "federalize", "suspended", "iron laws", "fight", "state power",
        "set the terms", "surrender",
    ],
    "sacred": [
        "god", "immortal", "sacrifice", "worthy", "brother", "heal", "awakened",
        "army", "dragon", "envy", "jealousy", "wickedness", "fire",
    ],
    "nation": [
        "america", "americans", "american", "nation", "country", "citizens",
        "united states", "border", "third world", "voters", "populace",
        "english", "foreign born",
    ],
    "management": [
        "team", "staff", "tolerate", "mission", "trains on the tracks", "role",
        "chief of staff", "leaks", "sanction", "termination", "solo", "star",
        "agreement", "context", "ballot", "campaign", "midterms", "successful",
    ],
    "affiliation": [
        "thank", "thank you", "family", "friends", "honor", "prayed",
        "supported", "commitment", "together", "lifetime", "see you",
    ],
    "evaluative": [
        "zealot", "conspiracy theorist", "odd duck", "ketamine", "whiffed",
        "alcoholic", "aghast", "political", "better leader", "personality",
        "finest", "disingenuously",
    ],
}

PRONOUNS = {
    "i": ["i", "me", "my", "mine", "myself", "i'm", "i've"],
    "we": ["we", "us", "our", "ours", "ourselves", "we're", "we've"],
    "you": ["you", "your", "yours", "you're", "you've"],
    "they": ["they", "them", "their", "theirs", "they're"],
    "he": ["he", "him", "his", "he's"],
}

TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?|\d[\d,]*")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower().replace("’", "'"))


def count_phrases(text: str, phrases: list[str]) -> int:
    """Count whole-word phrase matches (longest phrases first, no double count)."""
    t = " " + " ".join(tokenize(text)) + " "
    n = 0
    for p in sorted(phrases, key=len, reverse=True):
        pat = " " + " ".join(tokenize(p)) + " "
        k = t.count(pat)
        if k:
            n += k
            t = t.replace(pat, " | ")
    return n
