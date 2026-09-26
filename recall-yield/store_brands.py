"""Private-label brand dictionary, keyed by retailer.

Each retailer entry has:
  brands:  store-brand names that retailer owns
  firm:    regexes matching the retailer's own corporate names, used to tell
           "retailer recalled its own label" apart from "a maker recalled it"
  sold_at: regex for "sold at <retailer>" style mentions

Brands marked ambiguous are common words and only count when the text says
"<name> brand", "brand <name>", or quotes the name.
"""

RETAILERS = {
    "Costco": {
        "brands": ["Kirkland Signature", "Kirkland"],
        "firm": [r"costco"],
        "sold_at": r"costco",
    },
    "Walmart": {
        "brands": ["Great Value", "Marketside", "Freshness Guaranteed",
                   "Sam's Choice", "bettergoods", "Equate"],
        "firm": [r"wal-?mart"],
        "sold_at": r"wal-?mart",
    },
    "Sam's Club": {
        "brands": ["Member's Mark", "Members Mark"],
        "firm": [r"sam'?s (west|club)"],
        "sold_at": r"sam'?s club",
    },
    "Target": {
        "brands": ["Good & Gather", "Good and Gather", "Market Pantry",
                   "Favorite Day"],
        "firm": [r"\btarget corp"],
        "sold_at": r"\btarget\b",
    },
    "Kroger": {
        "brands": ["Kroger", "Simple Truth", "Private Selection",
                   "Home Chef", "Heritage Farm", "Smart Way"],
        "firm": [r"\bkroger\b", r"fred meyer", r"ralphs", r"king soopers",
                 r"harris teeter", r"smith'?s food"],
        "sold_at": r"kroger|fred meyer|ralphs|king soopers|harris teeter",
    },
    "Albertsons": {
        "brands": ["Signature Select", "Signature Cafe", "Signature Farms",
                   "O Organics", "Lucerne", "Open Nature", "Waterfront Bistro",
                   "Primo Taglio"],
        "firm": [r"albertsons", r"safeway", r"vons", r"jewel-?osco",
                 r"shaw'?s", r"acme markets"],
        "sold_at": r"albertsons|safeway|vons|jewel-?osco|acme markets",
    },
    "Whole Foods": {
        "brands": ["365 by Whole Foods", "365 Everyday Value",
                   "Whole Foods Market"],
        "firm": [r"whole foods?\b", r"\bwfm\b"],
        "sold_at": r"whole foods",
    },
    "Amazon": {
        "brands": ["Happy Belly", "Amazon Fresh", "Amazon Grocery",
                   "Amazon Kitchen"],
        "firm": [r"amazon"],
        "sold_at": r"amazon",
    },
    "Trader Joe's": {
        "brands": ["Trader Joe's", "Trader Joes", "Trader Jose's",
                   "Trader Giotto's", "Trader Ming's"],
        "firm": [r"trader joe"],
        "sold_at": r"trader joe",
    },
    "Aldi": {
        "brands": ["Simply Nature", "Millville", "Clancy's", "Friendly Farms",
                   "Happy Farms", "Specially Selected", "Appleton Farms",
                   "Kirkwood", "Park Street Deli", "Fit & Active",
                   "Never Any!", "Season's Choice", "Stonemill",
                   "Priano", "Mama Cozzi's", "Bremer", "Savoritz",
                   "Southern Grove", "Casa Mamita", "Earth Grown",
                   "Little Salad Bar", "L'oven Fresh", "Deutsche Küche"],
        "firm": [r"\baldi\b"],
        "sold_at": r"\baldi\b",
    },
    "Lidl": {
        "brands": ["Preferred Selection", "Lidl"],
        "firm": [r"\blidl\b"],
        "sold_at": r"\blidl\b",
    },
    "Ahold Delhaize": {
        "brands": ["Nature's Promise", "Taste of Inspirations",
                   "Food Lion", "Hannaford", "Stop & Shop",
                   "Giant", "Martin's"],
        "firm": [r"ahold", r"delhaize", r"food lion", r"hannaford",
                 r"stop & shop", r"giant food", r"\bgiant\b"],
        "sold_at": r"food lion|hannaford|stop & shop|giant food",
    },
    "Giant Eagle": {
        "brands": ["Giant Eagle", "Market District"],
        "firm": [r"giant eagle"],
        "sold_at": r"giant eagle",
    },
    "Publix": {
        "brands": ["Publix", "GreenWise"],
        "firm": [r"publix"],
        "sold_at": r"publix",
    },
    "H-E-B": {
        "brands": ["H-E-B", "HEB", "Hill Country Fare", "Central Market",
                   "Meal Simple"],
        "firm": [r"h-?e-?b\b", r"h\.e\. butt"],
        "sold_at": r"h-?e-?b\b",
    },
    "Hy-Vee": {
        "brands": ["Hy-Vee"],
        "firm": [r"hy-?vee"],
        "sold_at": r"hy-?vee",
    },
    "Wegmans": {
        "brands": ["Wegmans"],
        "firm": [r"wegmans"],
        "sold_at": r"wegmans",
    },
    "Meijer": {
        "brands": ["Meijer", "True Goodness", "Frederik's by Meijer"],
        "firm": [r"meijer"],
        "sold_at": r"meijer",
    },
    "Dollar General": {
        "brands": ["Clover Valley", "Good & Smart"],
        "firm": [r"dollar general", r"dolgencorp"],
        "sold_at": r"dollar general",
    },
    "Sprouts": {
        "brands": ["Sprouts Farmers Market", "Sprouts"],
        "firm": [r"sprouts farmers"],
        "sold_at": r"sprouts",
    },
    "Wakefern/ShopRite": {
        "brands": ["Bowl & Basket", "Wholesome Pantry", "ShopRite"],
        "firm": [r"wakefern", r"shoprite"],
        "sold_at": r"shoprite",
    },
    "UNFI/SuperValu": {
        "brands": ["Wild Harvest", "Essential Everyday", "Culinary Tours",
                   "Shoppers Value"],
        "firm": [r"\bunfi\b", r"united natural foods", r"supervalu"],
        "sold_at": None,
    },
    "Topco (co-op)": {
        "brands": ["Full Circle", "Food Club", "Top Care", "Paws Happy Life"],
        "firm": [r"topco"],
        "sold_at": None,
    },
    "Associated Wholesale Grocers": {
        "brands": ["Best Choice", "Always Save"],
        "firm": [r"associated wholesale grocers"],
        "sold_at": None,
    },
    "Western Family": {
        "brands": ["Western Family", "Shurfine", "Shur Fine"],
        "firm": [r"western family"],
        "sold_at": None,
    },
    "WinCo": {
        "brands": ["WinCo Foods", "WinCo"],
        "firm": [r"winco"],
        "sold_at": r"winco",
    },
    "Weis": {
        "brands": ["Weis Quality"],
        "firm": [r"weis markets"],
        "sold_at": r"weis markets",
    },
    "7-Eleven": {
        "brands": ["7-Select", "7 Select"],
        "firm": [r"7-eleven"],
        "sold_at": r"7-eleven",
    },
    "CVS": {
        "brands": ["Gold Emblem"],
        "firm": [r"\bcvs\b"],
        "sold_at": r"\bcvs\b",
    },
    "Walgreens": {
        "brands": ["Nice!"],
        "firm": [r"walgreen"],
        "sold_at": r"walgreens",
    },
}

# Common words that would false-positive without a "brand" cue.
AMBIGUOUS = {"Giant", "Kirkland", "Sprouts", "Nice!", "Full Circle",
             "Best Choice", "Heritage Farm", "Smart Way", "Always Save",
             "Earth Grown", "Never Any!", "Home Chef", "Central Market",
             "Lucerne", "Kirkwood", "Priano", "Bremer", "Lidl", "HEB",
             "Martin's", "Top Care", "Food Club"}
