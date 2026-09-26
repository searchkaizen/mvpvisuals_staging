# Store-brand extraction yield, 2025-09-01 to 2026-08-31

| Source | Recalls | maker_linked | retailer_self | sold_at_only | none | maker_linked % |
|---|---:|---:|---:|---:|---:|---:|
| FSIS | 0 | 0 | 0 | 0 | 0 | 0.0% |
| FDA human food | 532 | 39 | 12 | 2 | 479 | 7.3% |
| FDA pet/animal | 6 | 0 | 0 | 0 | 6 | 0.0% |
| ALL excl. pet | 532 | 39 | 12 | 2 | 479 | 7.3% |
| ALL | 538 | 39 | 12 | 2 | 485 | 7.2% |

FSIS maker_linked recalls that also carry an EST (plant) number: 0 of 0

## Pass bars

| Bar | Result | Pass |
|---|---|---|
| Unique retailer -> maker edges per year (excl. pet) >= 40 | 49.2 | yes |
| FSIS maker_linked recalls with a plant (EST) number >= 70% | 0% | no |
| Big five retailers with at least one edge (all five) | 5/5 (none missing) | yes |

Unique retailer -> maker edges: 49

| Retailer | Maker (recalling firm) | Recalls |
|---|---|---:|
| Kroger | Admiralty Island Fisheries | 2 |
| Whole Foods | WFM Purchasing | 2 |
| Wegmans | Mellace Family Brands California | 1 |
| Albertsons | Admiralty Island Fisheries | 1 |
| Publix | Admiralty Island Fisheries | 1 |
| WinCo | Admiralty Island Fisheries | 1 |
| Ahold Delhaize | Great Lakes Cheese | 1 |
| Aldi | Great Lakes Cheese | 1 |
| H-E-B | Great Lakes Cheese | 1 |
| Publix | Great Lakes Cheese | 1 |
| Sprouts | Great Lakes Cheese | 1 |
| Target | Great Lakes Cheese | 1 |
| Walmart | Great Lakes Cheese | 1 |
| Kroger | Moonlight Packing | 1 |
| Walmart | Beaver Street Fisheries | 1 |
| Walmart | FreshRealm | 1 |
| Wegmans | Pacific Coast Producers | 1 |
| Publix | The James Skinner | 1 |
| Publix | VENTURA FOODS | 1 |
| Aldi | Teasdale Foods | 1 |
| Sam's Club | MeriCal | 1 |
| H-E-B | Dollins Pecan | 1 |
| Costco | Western United Fish | 1 |
| Target | ONE FROZEN | 1 |
| Kroger | EGGS UNLIMITED | 1 |
| Walmart | EGGS UNLIMITED | 1 |
| Wegmans | Eli's Cheesecake | 1 |
| Target | JOHN B SANFILIPPO & SONS | 1 |
| Walmart | Rovira Biscuit | 1 |
| Kroger | MIDWEST POULTRY SERVC C/O H & LELECTRIC | 1 |
| Walmart | SAPUTO CHEESE USA | 1 |
| Kroger | Ajinomoto Foods North America | 1 |
| Trader Joe's | Ajinomoto Foods North America | 1 |
| Walmart | Taylor Farms de Mexico S. de R.L. de C.V | 1 |
| Ahold Delhaize | Legacy Bakehouse | 1 |
| Albertsons | DIRECT SOURCE SEAFOOD | 1 |
| Meijer | Bakkavor | 1 |
| Trader Joe's | Bakkavor | 1 |
| Aldi | LACTALIS CANADA | 1 |
| Walmart | United States Bakery | 1 |
| Meijer | Ferris Coffee and Nut | 1 |
| H-E-B | Plant Based Innovations | 1 |
| Kroger | Sugar Foods | 1 |
| Aldi | Dr. Praeger's Sensible Foods | 1 |
| Publix | ASK Foods | 1 |
| Whole Foods | Kettle Cuisine | 1 |
| Ahold Delhaize | Mount Olive Pickle | 1 |
| H-E-B | Bakkavor | 1 |
| Publix | Post Consumer Brands | 1 |

| Retailer | maker_linked recalls |
|---|---:|
| Walmart | 8 |
| Kroger | 7 |
| Publix | 6 |
| Aldi | 4 |
| H-E-B | 4 |
| Wegmans | 3 |
| Ahold Delhaize | 3 |
| Target | 3 |
| Whole Foods | 3 |
| Albertsons | 2 |
| Trader Joe's | 2 |
| Meijer | 2 |
| WinCo | 1 |
| Sprouts | 1 |
| Sam's Club | 1 |
| Costco | 1 |

Counts are unreviewed matches. Fill the `verdict` column in hits.csv, then run `python3 extract.py --score hits.csv` for precision.
