"""Shared settings: the six chiefs, their tenures, and how to recognize them in URLs and text."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = ROOT / "cache"          # downloaded sitemaps and article text (not committed)
FIGURES = ROOT / "figures"

# Miller has not served as chief yet; his row covers his time as deputy chief of staff.
CHIEFS = {
    "priebus":  dict(name="Reince Priebus", surname="Priebus",  start="2017-01-20", end="2017-07-31",
                     full=r"Reince Priebus"),
    "kelly":    dict(name="John Kelly",     surname="Kelly",    start="2017-07-31", end="2019-01-02",
                     full=r"John (F\. )?Kelly|Gen(\.|eral) Kelly",
                     not_url=r"kellyanne|megyn|mark-kelly|laura-kelly|r-kelly|clarkson|loeffler|kelly-craft|ayotte|sadler|ripa|ryan-kelly",
                     not_text=r"(Megyn|Mark|Laura|Ryan|R\.)\s+Kelly|Kelly(anne| Loeffler| Craft| Ayotte| Sadler| Clarkson)"),
    "mulvaney": dict(name="Mick Mulvaney",  surname="Mulvaney", start="2019-01-02", end="2020-03-31",
                     full=r"Mick Mulvaney"),
    "meadows":  dict(name="Mark Meadows",   surname="Meadows",  start="2020-03-31", end="2021-01-20",
                     full=r"Mark Meadows", not_url=r"meadowlands"),
    "wiles":    dict(name="Susie Wiles",    surname="Wiles",    start="2025-01-20", end="2026-11-06",
                     full=r"Susie Wiles|Susan Wiles"),
    "miller":   dict(name="Stephen Miller", surname="Miller",   start="2025-01-20", end="2026-11-06",
                     full=r"Stephen Miller",
                     not_url=r"katie-miller|jason-miller|miller-lite|judith-miller|dennis-miller|zell|brad-miller",
                     not_text=r"(Katie|Jason|Judith|Ross|Kathie|Dennis|Zell|Brad|Matt|Max|Cassidy|Chris|Mary|Tim|Carol|Greg)\s+Miller"),
}
ORDER = ["wiles", "kelly", "priebus", "meadows", "mulvaney", "miller"]
LABEL = {"wiles": "Wiles (2025–26)", "kelly": "Kelly (2017–19)", "priebus": "Priebus (2017)",
         "meadows": "Meadows (2020–21)", "mulvaney": "Mulvaney (2019–20)", "miller": "Miller (2025–26, deputy)"}

OUTLETS = {"cnn": "CNN", "nbc": "NBC News", "wex": "Washington Examiner"}
SAMPLE_PER_CHIEF = 50
