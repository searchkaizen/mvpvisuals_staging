# Store-brand recall extraction yield

**Results: see [FINDINGS.md](FINDINGS.md).** The workflow
`.github/workflows/recall-yield.yml` reruns everything on each push to this
branch and commits `results/`.

Tests one question before anything gets built: across 12 months of FSIS and FDA
recalls, how often does a recall name a store brand **and** a maker that isn't
the retailer? That pairing is a brand → maker edge. For FSIS recalls, the EST
number adds the plant.

## Prototype: "Who made this?"

`pantry/index.html` looks up a USDA plant number (from the round inspection
mark on meat, poultry and egg packages), a store brand, a retailer or a
company. It shows the plant, the company, the store brands recalls have tied
it to, and its recall history. `pantry/build_db.py` builds `pantry/db.json`
from the FSIS plant directory (`data/mpi_directory_2021.csv`, a 2021 copy,
because fsis.usda.gov blocks datacenter IPs), the FSIS recall snapshot and
`results/all-history/hits.csv`. To view it locally, run
`python3 -m http.server` in `pantry/` and open `localhost:8000`.

## Run

```sh
python3 extract.py                          # fetches api.fda.gov and fsis.usda.gov
python3 extract.py --start 2025-09-01 --end 2026-08-31 --out out
```

If those hosts are blocked, download the data yourself and pass the files in:

- FDA: `https://api.fda.gov/food/enforcement.json?search=report_date:[20250901+TO+20260831]&limit=1000`
  (add `&skip=1000` and so on if the total is over 1000, then merge the `results` arrays)
- FSIS: `https://www.fsis.usda.gov/fsis/api/recall/v/1`

```sh
python3 extract.py --fda fda.json --fsis fsis.json
```

## Output

- `out/summary.md` has the yield table by source and tier, the unique
  retailer → maker edges, and counts per retailer.
- `out/hits.csv` has every non-empty match, with a blank `verdict` column.
  Mark rows `y` or `n`, then run `python3 extract.py --score out/hits.csv` to
  get precision per tier.

## Tiers

| Tier | Meaning |
|---|---|
| `maker_linked` | Store brand named, and the recalling firm isn't the retailer. This is the yield that matters. |
| `retailer_self` | Store brand named, but the retailer is the recalling firm, so the maker is still hidden. |
| `sold_at_only` | No store brand, but the text says "sold at Walmart" or similar. The maker is known but the brand isn't. |
| `none` | Nothing usable. |

## Known limits

- The brand list in `store_brands.py` is hand-built and incomplete. A miss
  lowers the measured yield, so treat the result as a floor.
- A recalling firm isn't always the plant. FDA enforcement records list the
  recalling firm's city and state but no facility ID. Co-packers sometimes
  sit behind a distributor that does the recalling.
- FDA records are grouped by `event_id`, so the numbers count recall events,
  not individual products.
- Short or common-word brand names (Giant, Kirkland, Sprouts, and others)
  only match next to a "brand" cue or inside quotes. Those rows are the first
  place to look when reviewing.

## Tests

```sh
python3 -m unittest discover -s tests -v
```
