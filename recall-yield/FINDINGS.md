# Extraction-yield test: findings

**Verdict: the yield justifies building.** All three pass bars were set before
the data came in, and all three are cleared on both the last 12 months and the
full history.

| Bar (set in advance) | Last 12 months | Full history |
|---|---|---|
| Unique retailer → maker edges per year, excluding pet food, ≥ 40 | 51 | 54.5 / yr (807 edges total) |
| Meat and poultry (FSIS) maker-linked recalls that carry a plant number, ≥ 70% | 100% (2 of 2) | 90% (108 of 120) |
| Big five retailers (Costco, Walmart, Kroger, Aldi, Trader Joe's) each have at least one edge | 5 of 5 | 5 of 5 |

Data: 8,957 human-food recall events. That is 7,764 FDA events (Jan 2012 –
Aug 2026) plus 1,193 FSIS events (Jan 2014 – Nov 2025).

## What the numbers say

- **About 1 recall in 13 exposes a brand → maker link.** 7.4% of FDA recalls
  do, and 10.1% of FSIS recalls. That's about 50 new retailer → maker pairs a
  year. The rate held steady from 2015 to 2025, at 40–80 maker-linked
  recalls a year.
- **Across the full history there are 807 unique retailer → maker pairs.**
  Distinct makers found per retailer: Walmart 98, Trader Joe's 89, Kroger 74,
  Aldi 51, Ahold Delhaize 48, Albertsons 42, Target 42, Wegmans 39, Whole
  Foods 39, H-E-B 34, Publix 33, Meijer 32, Costco 19.
- **Meat and poultry recalls reach the plant.** 90% of FSIS maker-linked
  recalls print the plant number (P-17156 and so on), which completes the
  brand → maker → plant chain directly. FDA records give only the recalling
  firm's city and state, so non-meat products stop at the maker.
- **Costco is the weak spot.** Costco usually issues Kirkland recalls itself
  (the `retailer_self` tier), which keeps the maker hidden. Trader Joe's is
  the opposite: it almost never recalls under its own name, so its co-packers
  get exposed. It's the strongest showcase retailer.

## Accuracy

I hand-checked all 39 maker-linked FDA recalls from the last 12 months. After
fixing the two errors found (Whole Foods' own purchasing arm being counted as
a maker), 37 of 39 are correct links, and the other 2 are plausible but cut
off in the export. I skimmed all 120 FSIS maker-linked recalls. One was a
distributor rather than a maker (C&S Wholesale → Target). Precision is about
95%.

The yield is a floor. The brand list is hand-built (about 150 names), so
misses lower the count and don't inflate it.

## Caveats

- **FSIS data ends in Nov 2025.** FSIS's CDN blocks every datacenter IP, even
  from a real browser, so the FSIS numbers come from a public snapshot of the
  same API (github.com/deeptijaswal11/Food-Safety-Recall-Analysis). The
  12-month window therefore has only 13 FSIS recalls. Rerunning
  `extract.py` from a residential connection would bring it current.
- **The recalling firm is sometimes a distributor, not the maker.** This
  happened in about 1 in 40 of the matches reviewed.
- **Some FSIS recalls have no firm name.** 21 of the 120 lack one, and 17 of those do have a plant number, so they
  can be filled in from FSIS's MPI establishment
  directory, which maps plant number → company. That's a straightforward
  next join.

## Suggested next steps

1. Join plant numbers to the FSIS MPI directory to fill in missing maker
   names.
2. Expand the brand list, using Open Food Facts brand fields filtered to
   known retailer owners.
3. Add FDA press-release recalls. They name brands more consistently than
   the enforcement report does.

Raw outputs: `results/all-history/`, `results/last-12-months/`. Each folder
has `summary.md` plus `hits.csv`, which holds every match and a `verdict`
column for review.
