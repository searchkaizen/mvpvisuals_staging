#!/usr/bin/env python3
"""Extraction-yield test: how often do FSIS and FDA recalls expose the maker
behind a store brand?

Pulls 12 months of recalls (or reads saved JSON), finds store-brand mentions,
and sorts each recall into one tier:

  maker_linked    store brand named AND the recalling firm is not the retailer
                  -> gives a brand -> maker edge (plus a plant, for FSIS)
  retailer_self   store brand named but the retailer itself is the recalling
                  firm -> brand confirmed, maker still hidden
  sold_at_only    no store brand, but the text names a retailer as a point of
                  sale -> weak signal, maker is known but brand is not
  none            nothing usable

Standard library only. Usage:
  python3 extract.py                                  # fetch live
  python3 extract.py --fda fda.json --fsis fsis.json  # use saved downloads
"""

import argparse
import csv
import html
import os
import json
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import date, datetime

from store_brands import AMBIGUOUS, RETAILERS

FDA_URL = "https://api.fda.gov/food/enforcement.json"
FSIS_URL = "https://www.fsis.usda.gov/fsis/api/recall/v/1"
UA = "Mozilla/5.0 (recall-yield research script)"

EST_RE = re.compile(
    r"\bEST\.?\s*(?:No\.?\s*)?((?:[MPV][\s-]?)?\d{1,6}[A-Z]?)\b", re.I)
TAG_RE = re.compile(r"<[^>]+>")


# ---------- fetching ----------

def http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def fetch_fda(start, end):
    rows, skip = [], 0
    rng = f"report_date:[{start:%Y%m%d}+TO+{end:%Y%m%d}]"
    while True:
        data = http_json(f"{FDA_URL}?search={rng}&limit=1000&skip={skip}")
        batch = data.get("results", [])
        rows += batch
        total = data["meta"]["results"]["total"]
        skip += len(batch)
        if not batch or skip >= total:
            return rows


def fetch_fsis():
    return http_json(FSIS_URL)


# ---------- normalising ----------

def clean(text):
    return re.sub(r"\s+", " ", html.unescape(TAG_RE.sub(" ", text or ""))).strip()


def parse_date(s):
    for fmt in ("%Y%m%d", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(s[:10], fmt).date()
        except (TypeError, ValueError):
            pass
    return None


def fda_records(raw, start, end):
    """One record per recall event (FDA lists each product separately)."""
    events = defaultdict(list)
    for r in raw:
        d = parse_date(r.get("report_date"))
        if d and start <= d <= end:
            events[r.get("event_id") or r.get("recall_number")].append(r)
    for eid, items in events.items():
        first = items[0]
        yield {
            "source": "FDA",
            "id": eid,
            "date": str(parse_date(first.get("report_date"))),
            "firm": first.get("recalling_firm", ""),
            "firm_location": ", ".join(
                x for x in (first.get("city"), first.get("state")) if x),
            "text": " | ".join(
                i.get("product_description", "") for i in items),
            "context": first.get("reason_for_recall", "") + " "
                       + first.get("distribution_pattern", ""),
            "est": [],
            "n_products": len(items),
        }


def fsis_records(raw, start, end):
    for r in raw:
        if r.get("langcode", "English") != "English":
            continue
        d = parse_date(r.get("field_recall_date"))
        if not d or not (start <= d <= end):
            continue
        body = " ".join(clean(r.get(k)) for k in
                        ("field_title", "field_summary", "field_product_items"))
        yield {
            "source": "FSIS",
            "id": r.get("field_recall_number") or r.get("field_title"),
            "date": str(d),
            "firm": clean(r.get("field_establishment")),
            "firm_location": "",
            "text": body,
            "context": "",
            "est": sorted({e.upper().replace(" ", "") for e in EST_RE.findall(body)}),
            "n_products": 1,
            "type": r.get("field_recall_type", ""),
        }


# ---------- matching ----------

def _brand_pattern(name):
    esc = re.escape(name).replace(r"\ ", r"\s+").replace("'", "['’]?")
    core = rf"(?<![\w-]){esc}(?![\w-])"
    if name in AMBIGUOUS:
        # require a brand cue: "X brand", "brand X", or the name in quotes
        return re.compile(
            rf"{core}\s*(?:®|™)?\s+brand|brand(?:ed)?(?:\s+name)?\s*[:\"“]?\s*{core}"
            rf"|[\"“]{core}[\"”]", re.I)
    return re.compile(core, re.I)


BRAND_PATTERNS = [
    (ret, b, _brand_pattern(b))
    for ret, cfg in RETAILERS.items() for b in cfg["brands"]
]
FIRM_PATTERNS = {ret: [re.compile(p, re.I) for p in cfg["firm"]]
                 for ret, cfg in RETAILERS.items()}
SOLD_AT = {
    ret: re.compile(rf"(?:sold|available|distributed|purchased)\s+(?:\w+\s+){{0,6}}?"
                    rf"(?:at|in|to|from)\s+(?:\w+\s+){{0,4}}?(?:{cfg['sold_at']})", re.I)
    for ret, cfg in RETAILERS.items() if cfg["sold_at"]
}


def find_brands(text):
    hits = {}
    for ret, brand, pat in BRAND_PATTERNS:
        if pat.search(text):
            hits.setdefault(ret, set()).add(brand)
    return hits


def firm_is_retailer(firm, retailer):
    return any(p.search(firm or "") for p in FIRM_PATTERNS[retailer])


def classify(rec):
    brands = find_brands(rec["text"])
    out = dict(rec, retailers=sorted(brands), brands=sorted(
        b for bs in brands.values() for b in bs))
    if brands:
        makers = [r for r in brands if not firm_is_retailer(rec["firm"], r)]
        out["tier"] = "maker_linked" if makers else "retailer_self"
        out["linked_retailers"] = sorted(makers)
        return out
    blob = rec["text"] + " " + rec["context"]
    sold = sorted(r for r, p in SOLD_AT.items() if p.search(blob))
    out["linked_retailers"] = sold
    out["tier"] = "sold_at_only" if sold else "none"
    return out


# ---------- reporting ----------

TIERS = ["maker_linked", "retailer_self", "sold_at_only", "none"]


def report(results, start, end, outdir):
    by_src = defaultdict(list)
    for r in results:
        by_src[r["source"]].append(r)

    lines = [f"# Store-brand extraction yield, {start} to {end}", ""]
    lines += ["| Source | Recalls | " + " | ".join(TIERS) + " | maker_linked % |",
              "|---|---:|" + "---:|" * len(TIERS) + "---:|"]
    for src in ("FSIS", "FDA", "ALL"):
        rows = results if src == "ALL" else by_src[src]
        c = Counter(r["tier"] for r in rows)
        pct = 100 * c["maker_linked"] / len(rows) if rows else 0
        lines.append(f"| {src} | {len(rows)} | "
                     + " | ".join(str(c[t]) for t in TIERS) + f" | {pct:.1f}% |")

    fsis_linked = [r for r in by_src["FSIS"] if r["tier"] == "maker_linked"]
    with_est = sum(1 for r in fsis_linked if r["est"])
    lines += ["", f"FSIS maker_linked recalls that also carry an EST (plant) "
                  f"number: {with_est} of {len(fsis_linked)}"]

    edges = Counter()
    for r in results:
        if r["tier"] != "maker_linked":
            continue
        for ret in r["linked_retailers"]:
            edges[(ret, r["firm"])] += 1
    lines += ["", f"Unique retailer -> maker edges: {len(edges)}", "",
              "| Retailer | Maker (recalling firm) | Recalls |", "|---|---|---:|"]
    lines += [f"| {ret} | {firm} | {n} |"
              for (ret, firm), n in sorted(edges.items(), key=lambda x: -x[1])]

    per_ret = Counter(ret for r in results if r["tier"] == "maker_linked"
                      for ret in r["linked_retailers"])
    lines += ["", "| Retailer | maker_linked recalls |", "|---|---:|"]
    lines += [f"| {k} | {v} |" for k, v in per_ret.most_common()]
    lines += ["", "Counts are unreviewed matches. Fill the `verdict` column in "
                  "hits.csv, then run `python3 extract.py --score hits.csv` "
                  "for precision."]

    with open(f"{outdir}/summary.md", "w") as f:
        f.write("\n".join(lines) + "\n")

    fields = ["verdict", "tier", "source", "id", "date", "firm", "firm_location",
              "retailers", "brands", "est", "text"]
    with open(f"{outdir}/hits.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in sorted(results, key=lambda r: (TIERS.index(r["tier"]), r["date"])):
            if r["tier"] == "none":
                continue
            w.writerow(dict(r, verdict="", retailers=";".join(r["retailers"]),
                            brands=";".join(r["brands"]), est=";".join(r["est"]),
                            text=r["text"][:1500]))
    print("\n".join(lines[:9]))
    print(f"\nWrote {outdir}/summary.md and {outdir}/hits.csv")


def score(path):
    """Precision from a hand-reviewed hits.csv (verdict: y / n)."""
    c = defaultdict(Counter)
    with open(path) as f:
        for row in csv.DictReader(f):
            v = row["verdict"].strip().lower()[:1]
            if v in ("y", "n"):
                c[row["tier"]][v] += 1
    for tier, n in c.items():
        tot = n["y"] + n["n"]
        print(f"{tier}: {n['y']}/{tot} correct ({100 * n['y'] / tot:.0f}%)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", default="2025-09-01")
    ap.add_argument("--end", default="2026-08-31")
    ap.add_argument("--fda", help="saved openFDA food enforcement JSON")
    ap.add_argument("--fsis", help="saved FSIS recall API JSON")
    ap.add_argument("--out", default="out")
    ap.add_argument("--score", help="score a reviewed hits.csv and exit")
    a = ap.parse_args()
    if a.score:
        return score(a.score)

    start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)

    def load(path):
        with open(path) as f:
            data = json.load(f)
        return data.get("results", data) if isinstance(data, dict) else data

    fda_raw = load(a.fda) if a.fda else fetch_fda(start, end)
    fsis_raw = load(a.fsis) if a.fsis else fetch_fsis()

    os.makedirs(a.out, exist_ok=True)
    results = [classify(r) for r in
               list(fsis_records(fsis_raw, start, end))
               + list(fda_records(fda_raw, start, end))]
    report(results, start, end, a.out)


if __name__ == "__main__":
    sys.exit(main())
