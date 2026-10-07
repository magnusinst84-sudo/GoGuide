#!/usr/bin/env python3
"""Record ONE verified fact for a career. Run after you opened the page yourself.

  python scripts/mark_verified.py <career_id> <field> <value> <url> "<exact text from the page>"

Example:
  python scripts/mark_verified.py btech-cse-private tuition_per_year 275000 \
     "https://www.srmist.edu.in/some/fee-page" "B.Tech CSE tuition Rs 2,75,000 per year" --note "fee category: general"

Does 4 things: sets the value, writes the source (URL + date + quote), removes the field from
estimated_fields, and appends a line to data/SOURCES_LOG.md. Refuses homepages and empty quotes.
"""
import json, sys, pathlib, datetime, argparse
from urllib.parse import urlparse

ap = argparse.ArgumentParser()
ap.add_argument("career_id"); ap.add_argument("field"); ap.add_argument("value")
ap.add_argument("url"); ap.add_argument("quote")
ap.add_argument("--note", default=""); ap.add_argument("--data", default="data")
a = ap.parse_args()

u = urlparse(a.url)
if u.scheme not in ("http", "https") or not u.netloc: sys.exit("ERROR: url must start with http(s)://")
if u.path.strip("/") == "" and not u.query: sys.exit("ERROR: that is a homepage. Use the specific page URL.")
if len(a.quote.strip()) < 8: sys.exit("ERROR: paste the exact text from the page (at least a short sentence).")

d = pathlib.Path(a.data); p = d / "careers.json"
careers = json.loads(p.read_text(encoding="utf-8"))
c = next((x for x in careers if x["id"] == a.career_id), None)
if c is None: sys.exit(f"ERROR: no career '{a.career_id}'")
try: val = json.loads(a.value)
except Exception: val = a.value

parts = a.field.split(".")
if len(parts) == 1:
    if parts[0] not in c: sys.exit(f"ERROR: unknown field '{a.field}'")
    c[parts[0]] = val
elif len(parts) == 2:
    if parts[0] not in c or not isinstance(c[parts[0]], dict): sys.exit(f"ERROR: unknown field '{a.field}'")
    c[parts[0]][parts[1]] = val
else: sys.exit("ERROR: field can have at most one dot (e.g. salary.y1 or city_demand.Chennai)")

today = datetime.date.today().isoformat()
c.setdefault("sources", {})[a.field] = f'{a.url} (accessed {today}) - VERIFIED: "{a.quote.strip()}"' + (f" [{a.note}]" if a.note else "")
est = c.setdefault("estimated_fields", [])
removed = a.field in est
if removed: est.remove(a.field)
elif parts[0] in est and len(parts) == 2:
    print(f"NOTE: '{parts[0]}' as a whole is still marked estimate; remove it by hand once all its parts are verified.")

p.write_text(json.dumps(careers, indent=2, ensure_ascii=False), encoding="utf-8")
log = d / "SOURCES_LOG.md"
if not log.exists(): log.write_text("# Sources log\n\n| URL | What I took | Date accessed | Fields it supports |\n|---|---|---|---|\n", encoding="utf-8")
with log.open("a", encoding="utf-8") as f:
    f.write(f'| {a.url} | "{a.quote.strip()}" | {today} | {a.career_id}.{a.field} |\n')
print(f"OK {a.career_id}.{a.field} = {val!r}  (estimate label removed: {removed})")
print("Now run: python scripts/validate_data.py data --report")
