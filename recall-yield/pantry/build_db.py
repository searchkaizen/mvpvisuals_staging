#!/usr/bin/env python3
"""Build the lookup database behind the "who made this?" prototype.

Joins three sources into one JSON file:
  1. FSIS plant directory (EST number -> company, address, activities)
  2. FSIS recalls (EST number + firm + store brands, 2014 on)
  3. FDA store-brand recall matches from extract.py (maker -> store brands)

  python3 pantry/build_db.py --directory data/mpi_directory_2021.csv \
      --fsis raw/fsis.json --fda-hits results/all-history/hits.csv \
      --out pantry/db.json
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from extract import classify, fsis_records, norm_firm  # noqa: E402

EST_TOKEN = re.compile(r"([MPVIG])?\s*-?\s*(\d{1,6})\s*([A-Z])?\b", re.I)


def plant_keys(raw):
    """'M46712+P46712' or 'P-7345A' or '17156' -> ['M46712', 'P46712']."""
    keys = []
    for part in re.split(r"[+;,/]|\s&\s", raw or ""):
        m = EST_TOKEN.search(part.upper().replace("EST.", "").replace("EST", ""))
        if m:
            keys.append(f"{m.group(1) or ''}{m.group(2)}{m.group(3) or ''}")
    return keys


def bare(key):
    return key.lstrip("MPVIG")


def resolver_index(plants):
    index = defaultdict(list)
    for k in sorted(plants):
        index[bare(k)].append(k)
    return index


def resolver(plants):
    """Labels often print '17156' for directory entries 'M17156'/'P17156'."""
    index = resolver_index(plants)

    def resolve(key):
        if key in plants:
            return [key]
        return sorted(index.get(bare(key), [])) or [key]
    return resolve


def maker_key(name):
    return re.sub(r"[^a-z0-9]+", " ", norm_firm(name).lower()).strip()


def load_directory(path):
    plants = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            rec = {
                "company": r["company"].strip(),
                "address": ", ".join(x.strip() for x in
                                     (r["street"], r["city"], f'{r["st"]} {r["zip"]}') if x.strip()),
                "activities": r["activities"].strip(),
                "dba": r["dbas"].strip(),
                "source": "FSIS directory (2021 copy)",
            }
            for k in plant_keys(r["est_number"]):
                plants[k] = rec
    return plants


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--directory", required=True)
    ap.add_argument("--fsis", required=True)
    ap.add_argument("--fda-hits", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    plants = load_directory(a.directory)
    n_dir = len(plants)
    resolve = resolver(plants)
    makers = defaultdict(lambda: {"name": "", "plants": set(), "brands": defaultdict(set),
                                  "recalls": []})
    recalls = {}

    def add_maker(name, rec_id, retailers, brands, ests):
        if not name:
            return None
        k = maker_key(name)
        m = makers[k]
        m["name"] = m["name"] or name
        m["plants"].update(ests)
        for ret in retailers:
            m["brands"][ret].update(b for b in brands if b)
        if rec_id not in m["recalls"]:
            m["recalls"].append(rec_id)
        return k

    # FSIS recalls: every one goes into the plant's history, store brand or not.
    with open(a.fsis) as f:
        raw = json.load(f)
    raw = raw.get("results", raw) if isinstance(raw, dict) else raw
    filled = 0
    for rec in fsis_records(raw, date(2000, 1, 1), date(2100, 1, 1)):
        r = classify(rec)
        ests = sorted({x for e in r["est"] for k in plant_keys(e) for x in resolve(k)})
        firm = r["firm"]
        if not firm:  # fill the maker from the plant directory
            for e in ests:
                if e in plants:
                    firm, filled = plants[e]["company"], filled + 1
                    break
        rid = f"FSIS {r['id']}"
        linked = r["linked_retailers"] if r["tier"] == "maker_linked" else []
        recalls[rid] = {"date": r["date"], "source": "FSIS", "firm": firm,
                        "tier": r["tier"], "retailers": linked, "brands": r["brands"],
                        "plants": ests, "text": r["text"][:300]}
        mk = add_maker(firm, rid, linked, r["brands"], ests)
        for e in ests:  # recall-printed plants the 2021 directory lacks
            plants.setdefault(e, {"company": firm, "address": "", "activities": "",
                                  "dba": "", "source": "FSIS recall notice"})
        recalls[rid]["maker"] = mk

    # FDA store-brand recalls (no plant numbers; maker = recalling firm)
    with open(a.fda_hits) as f:
        for r in csv.DictReader(f):
            if r["source"] != "FDA" or r["tier"] not in ("maker_linked", "retailer_self"):
                continue
            rid = f"FDA event {r['id']}"
            rets = r["retailers"].split(";") if r["tier"] == "maker_linked" else []
            brands = r["brands"].split(";")
            recalls[rid] = {"date": r["date"], "source": "FDA", "firm": r["firm"],
                            "location": r["firm_location"], "tier": r["tier"],
                            "retailers": rets, "brands": brands, "plants": [],
                            "text": r["text"][:300]}
            recalls[rid]["maker"] = add_maker(r["firm"], rid, rets, brands, [])

    # Plant -> maker link, so a plant lookup can show that maker's store brands.
    for k, m in makers.items():
        for e in m["plants"]:
            if e in plants:
                plants[e].setdefault("makers", [])
                if k not in plants[e]["makers"]:
                    plants[e]["makers"].append(k)
    for e, p in plants.items():
        dk = maker_key(p["company"])
        if dk in makers:
            p.setdefault("makers", [])
            if dk not in p["makers"]:
                p["makers"].insert(0, dk)

    # M/P/V keys of one directory row share a record; store it once.
    sites, plant_idx, seen = [], {}, {}
    for k, p in sorted(plants.items()):
        if id(p) not in seen:
            seen[id(p)] = len(sites)
            sites.append(p)
        plant_idx[k] = seen[id(p)]

    retailers = defaultdict(set)
    for k, m in makers.items():
        for ret in m["brands"]:
            retailers[ret].add(k)

    out = {
        "built": str(date.today()),
        "sources": {
            "directory": "FSIS Meat, Poultry and Egg Product Inspection Directory (2021 copy)",
            "fsis": "FSIS recall API snapshot, 2014-01 to 2025-11",
            "fda": "openFDA food enforcement reports, 2012-01 to 2026-08",
        },
        "sites": sites,
        "plants": plant_idx,
        "makers": {k: {"name": m["name"], "plants": sorted(m["plants"]),
                       "brands": {r: sorted(b) for r, b in m["brands"].items()},
                       "recalls": sorted(m["recalls"], key=lambda x: recalls[x]["date"],
                                         reverse=True)}
                   for k, m in makers.items()},
        "recalls": recalls,
        "retailers": {r: sorted(v) for r, v in sorted(retailers.items())},
    }
    with open(a.out, "w") as f:
        json.dump(out, f, separators=(",", ":"))

    linked = sum(1 for m in out["makers"].values() if m["brands"])
    print(f"plants: {len(plants)} ({n_dir} from directory, "
          f"{len(plants) - n_dir} added from recall notices)")
    print(f"makers: {len(makers)} ({linked} with store-brand links); "
          f"recalls: {len(recalls)}; FSIS firms filled from directory: {filled}")
    print(f"wrote {a.out} ({os.path.getsize(a.out) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
