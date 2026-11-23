"""Terminal menu for Quote of the Day. Run: python cli.py"""
from core import analytics, export
from core import search as finder
from core.api_client import get_quote
from core.config import EXPORT_DIR
from core.models import CATEGORIES, Quote
from core.plots import CHARTS
from core.storage import DuplicateError, Storage
from core.validators import (ValidationError, clean_author, clean_category, clean_rating, clean_text)

G, A, R, D, X = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m"
store = Storage()


def ask(prompt, cleaner, optional=False):
    """Loop until the cleaner accepts the input."""
    while True:
        raw = input(f"{prompt}: ").strip()
        if optional and not raw:
            return None
        try:
            return cleaner(raw)
        except ValidationError as e:
            print(f"{R}  {e}{X}")


def show_table(quotes, per_page=8):
    if not quotes:
        print(f"{D}No quotes to show.{X}")
        return
    page = 1
    while True:
        rows, page, pages = finder.paginate(quotes, page, per_page)
        print(f"\n{'ID':<9}{'Category':<12}{'Rate':<6}{'Author':<24}Quote")
        print("-" * 78)
        for q in rows:
            text = q.text if len(q.text) <= 40 else q.text[:37] + "..."
            print(f"{q.id:<9}{q.category:<12}{q.rating or '-':<6}{q.author[:22]:<24}{text}")
        if pages == 1:
            return
        cmd = input(f"\nPage {page}/{pages}  [n]ext [p]rev [q]uit: ").strip().lower()
        if cmd == "n":
            page += 1
        elif cmd == "p":
            page -= 1
        else:
            return


def new_quote():
    q = get_quote()
    print(f"\n  {G}“{q.text}”{X}\n  {D}— {q.author} ({q.source}){X}\n")
    if input("Save to favorites? [y/N]: ").lower().startswith("y"):
        print("Categories:", ", ".join(CATEGORIES))
        q.category = ask(f"Category [{q.category}]", lambda v: clean_category(v or q.category))
        q.rating = ask("Rating 1-5 (Enter to skip)", clean_rating, optional=True)
        try:
            store.add(q)
            print(f"{G}Saved.{X}")
        except DuplicateError as e:
            print(f"{A}{e}{X}")


def add_manual():
    text = ask("Quote", clean_text)
    author = ask("Author", clean_author)
    print("Categories:", ", ".join(CATEGORIES))
    cat = ask("Category", clean_category)
    rating = ask("Rating 1-5 (Enter to skip)", clean_rating, optional=True)
    try:
        store.add(Quote(text=text, author=author, category=cat, rating=rating))
        print(f"{G}Saved.{X}")
    except DuplicateError as e:
        print(f"{A}{e}{X}")


def find():
    kw = input("Keyword (Enter to skip): ")
    cat = input(f"Category ({', '.join(CATEGORIES)}; Enter to skip): ").strip()
    cat = cat.title() if cat.title() in CATEGORIES else ""
    show_table(finder.search(store.load(), keyword=kw, category=cat))


def delete():
    qid = input("ID to delete: ").strip()
    print(f"{G}Deleted.{X}" if store.delete(qid) else f"{R}No quote with that ID.{X}")


def summary():
    quotes = store.load()
    s = analytics.summarize(quotes)
    print(f"\nTotal: {s['total']}   Average rating: {s['avg_rating'] or 'n/a'}   Last 7 days: {s['recent_7']}")
    for k, v in s["by_category"].items():
        print(f"  {k:<12}{'#' * v} {v}")
    print("Top authors:", ", ".join(f"{a} ({n})" for a, n in s["top_authors"]) or "none")
    for w in s["warnings"]:
        print(f"{A}  ! {w}{X}")


def export_all():
    quotes = store.load()
    s = analytics.summarize(quotes)
    EXPORT_DIR.mkdir(exist_ok=True)
    for name, fn in (("report.md", export.markdown), ("audit.txt", export.text_log), ("quotes.csv", export.csv_text)):
        (EXPORT_DIR / name).write_text(fn(quotes, s), encoding="utf-8")
    for name, fn in CHARTS.items():
        (EXPORT_DIR / f"{name}.png").write_bytes(fn(s))
    print(f"{G}Reports and charts written to {EXPORT_DIR}{X}")


def import_csv():
    path = input("CSV path: ").strip().strip('"')
    try:
        text = open(path, encoding="utf-8-sig").read()
    except OSError as e:
        print(f"{R}Can’t read that file: {e.strerror}{X}")
        return
    r = store.import_csv(text)
    print(f"Imported {r.added} of {r.total} rows.")
    for e in r.errors:
        print(f"{R}  {e}{X}")


MENU = [("Get a new quote", new_quote), ("Add a quote manually", add_manual), ("Browse and search favorites", find),
        ("Delete a quote", delete), ("Summary", summary), ("Export reports and charts", export_all),
        ("Import from CSV", import_csv)]


def main():
    print(f"\n{G}  Quote of the Day{X}\n  {D}Fetch quotes, keep the ones you love.{X}")
    while True:
        print()
        for i, (label, _) in enumerate(MENU, 1):
            print(f"  {i}. {label}")
        print("  0. Quit")
        choice = input("\nChoose: ").strip()
        if choice == "0":
            return
        if choice.isdigit() and 1 <= int(choice) <= len(MENU):
            try:
                MENU[int(choice) - 1][1]()
            except (KeyboardInterrupt, EOFError):
                print("\nCancelled.")
        else:
            print(f"{R}Pick a number from the menu.{X}")


if __name__ == "__main__":
    main()
