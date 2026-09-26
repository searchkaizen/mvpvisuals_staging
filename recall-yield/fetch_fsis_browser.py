"""Fetch the FSIS recall API through a real browser session.

FSIS's CDN rejects plain HTTP clients from datacenter IPs. Loading the
recalls page first gives the browser the cookies the CDN expects; the API
call then runs from inside that page.

  pip install playwright && playwright install --with-deps chromium
  python3 fetch_fsis_browser.py raw/fsis.json
"""

import json
import sys

from playwright.sync_api import sync_playwright

API = "/fsis/api/recall/v/1"


def main(out):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(locale="en-US")
        resp = page.goto("https://www.fsis.usda.gov/recalls", wait_until="domcontentloaded",
                         timeout=90_000)
        print(f"recalls page: HTTP {resp.status if resp else '?'}")
        status, body = page.evaluate(
            "async u => { const r = await fetch(u, {headers: {Accept: 'application/json'}});"
            " return [r.status, await r.text()]; }", API)
        browser.close()
    print(f"API: HTTP {status}, {len(body)} bytes")
    data = json.loads(body)  # raises if we got the CDN's HTML error page
    with open(out, "w") as f:
        json.dump(data, f)
    print(f"saved {len(data)} FSIS records to {out}")


if __name__ == "__main__":
    main(sys.argv[1])
