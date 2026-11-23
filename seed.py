"""Generate demo data. Usage: python seed.py [--load]   (--load also fills data/quotes.json)"""
import csv
import json
import random
import sys
from datetime import datetime, timedelta

from core.config import DATA_DIR, QUOTES_FILE
from core.export import FIELDS
from core.models import Quote
from core.storage import Storage

SEED_REAL = [
    ("The unexamined life is not worth living.", "Socrates", "Wisdom"),
    ("I think, therefore I am.", "René Descartes", "Wisdom"),
    ("The journey of a thousand miles begins with a single step.", "Lao Tzu", "Wisdom"),
    ("We are what we repeatedly do. Excellence, then, is not an act, but a habit.", "Will Durant", "Motivation"),
    ("On ne voit bien qu’avec le cœur.", "Antoine de Saint-Exupéry", "Life"),
    ("Stay hungry, stay foolish.", "Steve Jobs", "Motivation"),
    ("Well done is better than well said.", "Benjamin Franklin", "Motivation"),
    ("Do what you can, with what you have, where you are.", "Theodore Roosevelt", "Motivation"),
    ("Courage is grace under pressure.", "Ernest Hemingway", "Courage"),
    ("The best way to predict the future is to invent it.", "Alan Kay", "Technology"),
    ("Premature optimization is the root of all evil.", "Donald Knuth", "Technology"),
    ("Talk is cheap. Show me the code.", "Linus Torvalds", "Technology"),
    ("Simplicity is prerequisite for reliability.", "Edsger W. Dijkstra", "Technology"),
    ("Keep close to Nature’s heart.", "John Muir", "Nature"),
    ("In every walk with nature one receives far more than he seeks.", "John Muir", "Nature"),
    ("The earth laughs in flowers.", "Ralph Waldo Emerson", "Nature"),
    ("Imagination is more important than knowledge.", "Albert Einstein", "Wisdom"),
    ("No man is an island.", "John Donne", "Life"),
    ("To thine own self be true.", "William Shakespeare", "Life"),
    ("Fall seven times, stand up eight.", "Japanese proverb", "Courage"),
    ("Programs must be written for people to read, and only incidentally for machines to execute.",
     "Harold Abelson", "Technology"),
    ("The only way to do great work is to love what you do.", "Steve Jobs", "Motivation"),
    ("Early to bed and early to rise makes a man healthy, wealthy, and wise.", "Benjamin Franklin", "Life"),
    ("Brevity is the soul of wit.", "William Shakespeare", "Wisdom"),
    ("The pen is mightier than the sword.", "Edward Bulwer-Lytton", "Wisdom"),
    ("Software is eating the world.", "Marc Andreessen", "Technology"),
    ("Make it work, make it right, make it fast.", "Kent Beck", "Technology"),
    ("Any sufficiently advanced technology is indistinguishable from magic.", "Arthur C. Clarke", "Technology"),
]
EDGE = [
    ((("Small steps compound into remarkable change. " * 12)[:499] + "."), "Unknown", "Motivation"),  # exactly 500 chars
    ("Be brave.", "Unknown", "Courage"),  # short quote
]
MOCK_REAL = [
    ("Nature does not hurry, yet everything is accomplished.", "Lao Tzu", "Nature"),
    ("The only thing we have to fear is fear itself.", "Franklin D. Roosevelt", "Courage"),
    ("Not all those who wander are lost.", "J. R. R. Tolkien", "Life"),
    ("A rolling stone gathers no moss.", "Proverb", "Wisdom"),
    ("Rome wasn’t built in a day.", "Proverb", "Motivation"),
    ("Actions speak louder than words.", "Proverb", "Wisdom"),
    ("Where there is a will, there is a way.", "Proverb", "Motivation"),
    ("This too shall pass.", "Unknown", "Life"),
    ("Knowledge is power.", "Francis Bacon", "Wisdom"),
    ("Hope is the thing with feathers.", "Emily Dickinson", "Life"),
    ("Debugging is twice as hard as writing the code in the first place.", "Brian Kernighan", "Technology"),
    ("The sea, once it casts its spell, holds one in its net of wonder forever.", "Jacques Cousteau", "Nature"),
    ("In nature nothing exists alone.", "Rachel Carson", "Nature"),
    ("The Earth is what we all have in common.", "Wendell Berry", "Nature"),
]
LEGACY_CSV = """text,author,category,rating,saved_at
Fortune favors the prepared mind.,Louis Pasteur,Wisdom,5,2026-11-01T09:00:00
Energy and persistence conquer all things.,Benjamin Franklin,Motivation,4,2026-11-02T10:30:00
"Whatever you are, be a good one.",Abraham Lincoln,Life,,2026-11-03
,Nobody,Life,3,2026-11-04T08:00:00
A valid quote with a bad rating.,Some Author,Life,9,2026-11-05T08:00:00
A valid quote with a bad category.,Some Author,Sports,3,2026-11-05T08:00:00
No author on this one.,,Life,3,2026-11-06T08:00:00
Talk is cheap. Show me the code.,Linus Torvalds,Technology,5,2026-11-07T08:00:00
Rating is not a number.,Some Author,Life,abc,2026-11-08T08:00:00
Time is the wisest counselor.,Pericles,Wisdom,4,not-a-date
"""


def build(entries, rng, spread=False):
    now = datetime.now()
    out = []
    for text, author, cat in entries:
        q = Quote(text=text, author=author, category=cat, source="mock")
        q.rating = rng.choice([5, 5, 4, 4, 4, 3, 3, 2, 1, None, None])
        q.saved_at = (now - timedelta(days=rng.randint(0, 27), hours=rng.randint(0, 23),
                                      minutes=rng.randint(0, 59))).isoformat(timespec="seconds")
        out.append(q)
    return out


def main():
    rng = random.Random(113)
    quotes = sorted(build(SEED_REAL + EDGE, rng), key=lambda q: q.saved_at)
    DATA_DIR.mkdir(exist_ok=True)
    Storage(DATA_DIR / "sample_quotes.json")._write(quotes)
    with open(DATA_DIR / "sample_quotes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(q.to_dict() for q in quotes)
    (DATA_DIR / "mock_cache.json").write_text(
        json.dumps([dict(text=t, author=a, category=c) for t, a, c in MOCK_REAL], ensure_ascii=False, indent=2),
        encoding="utf-8")
    (DATA_DIR / "legacy_import_sample.csv").write_text(LEGACY_CSV, encoding="utf-8")
    if "--load" in sys.argv:
        Storage(QUOTES_FILE)._write(quotes)
    print(f"Wrote {len(quotes)} sample quotes, {len(MOCK_REAL)} mock-cache quotes"
          + (" and loaded data/quotes.json." if "--load" in sys.argv else "."))


if __name__ == "__main__":
    main()
