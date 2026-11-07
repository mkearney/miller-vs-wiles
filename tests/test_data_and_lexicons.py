import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mvw.lexicons import count_phrases, tokenize  # noqa: E402

REQUIRED = {"id", "speaker", "date", "text", "channel", "quote_status", "function", "target", "stance", "source_url"}
STATUSES = {"full", "fragment", "stitched", "paraphrase", "third_party_report"}


def _rows(name):
    return [json.loads(line) for line in (ROOT / "data" / name).read_text().splitlines() if line.strip()]


def test_utterance_schema():
    rows = _rows("utterances.jsonl")
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    for r in rows:
        assert REQUIRED <= r.keys(), r["id"]
        assert r["speaker"] in {"wiles", "miller"}
        assert r["quote_status"] in STATUSES
        assert r["source_url"].startswith("https://")
        assert r["stance"] in {"accelerator", "brake", "neutral"}


def test_perception_scale():
    for r in _rows("perceptions.jsonl"):
        for k in ("warmth", "competence", "dominance"):
            assert r[k] in (-1, 0, 1)
        assert r["alignment"] in {"ally", "critic", "neutral"}


def test_phrase_counting_no_double_count():
    assert count_phrases("To be crystal clear, I am clear.", ["clear", "crystal clear"]) == 2
    assert count_phrases("terrorists and terror", ["terror", "terrorists"]) == 2
    assert tokenize("Nobody’s going") == ["nobody's", "going"]
