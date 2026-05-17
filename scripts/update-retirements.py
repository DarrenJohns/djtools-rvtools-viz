#!/usr/bin/env python3
"""
Fetches Azure VM SKU retirement data from Microsoft Learn pages and updates
data/retirements.json with any new findings. Preserves existing entries.
"""

import json
import os
import re
import sys
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "data", "retirements.json")

RETIREMENT_PAGE = "https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-retirement"
PREV_GEN_PAGE = "https://learn.microsoft.com/en-us/azure/virtual-machines/sizes-previous-gen"

# Known mapping from series names to Azure family keys (lowercase).
# This helps match scraped series names to the family identifiers used in SKU data.
SERIES_TO_FAMILY = {
    "av2": "standardav2family",
    "amv2": "standardamv2family",
    "b v1": "standardbsfamily",
    "bs": "standardbsfamily",
    "ds": "standarddsfamily",
    "d": "standarddfamily",
    "dsv2": "standarddsv2family",
    "dsv2 promo": "standarddsv2promofamily",
    "dv2": "standarddv2family",
    "dv2 promo": "standarddv2promofamily",
    "dv3": "standarddv3family",
    "dsv3": "standarddsv3family",
    "ev3": "standardev3family",
    "esv3": "standardesv3family",
    "fv1": "standardfv1family",
    "fsv2": "standardfsv2family",
    "nv": "standardnvfamily",
    "ncv2": "standardncv2family",
    "ncv3": "standardncv3family",
    "nd": "standardndfamily",
    "ndv2": "standardndv2family",
    "h": "standardhfamily",
    "hb": "standardhbfamily",
    "hc": "standardhcfamily",
    "ls": "standardlsfamily",
    "lsv2": "standardlsv2family",
    "m": "standardmfamily",
    "mv2": "standardmv2family",
}

# Month names for date parsing
MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]


def load_existing():
    """Load existing retirements.json, or return empty structure."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"lastUpdated": "", "source": RETIREMENT_PAGE, "retirements": []}


def save_data(data):
    """Write retirements.json with updated timestamp."""
    data["lastUpdated"] = date.today().isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def guess_family_key(series_name):
    """Try to derive a family key from a series name like 'Av2-series'."""
    cleaned = series_name.lower().replace("-series", "").replace(" series", "").strip()
    if cleaned in SERIES_TO_FAMILY:
        return SERIES_TO_FAMILY[cleaned]
    # Fallback: construct key as 'standard<name>family'
    slug = re.sub(r"[^a-z0-9]", "", cleaned)
    return f"standard{slug}family"


def parse_retirement_date(text):
    """Extract a date like 'November 2028' from text."""
    for month in MONTHS:
        pattern = rf"({month})\s+(\d{{4}})"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"{match.group(1).capitalize()} {match.group(2)}"
    return None


def fetch_and_parse():
    """Fetch retirement pages and extract series + dates."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("[ERROR] Missing dependencies. Install with: pip install requests beautifulsoup4")
        sys.exit(1)

    found = {}  # family_key -> {name, retireDate, learnMoreUrl}

    # --- Parse main retirement page ---
    print(f"[INFO] Fetching {RETIREMENT_PAGE}")
    try:
        resp = requests.get(RETIREMENT_PAGE, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Look for table rows with series names and retirement dates
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) < 2:
                    continue
                text = " ".join(c.get_text(strip=True) for c in cells)

                # Look for series patterns like "Av2-series" or "Av2 series"
                series_match = re.search(r"([A-Za-z]+(?:v\d+)?(?:\s+(?:Promo|v\d+))?)\s*[-–]?\s*series", text, re.IGNORECASE)
                if not series_match:
                    continue

                series_name = series_match.group(0).strip()
                retire_date = parse_retirement_date(text)
                if not retire_date:
                    continue

                family_key = guess_family_key(series_name)
                link = cells[0].find("a")
                learn_url = link["href"] if link and link.get("href") else PREV_GEN_PAGE
                if learn_url.startswith("/"):
                    learn_url = "https://learn.microsoft.com" + learn_url

                found[family_key] = {
                    "name": series_name,
                    "retireDate": retire_date,
                    "learnMoreUrl": learn_url,
                }

        # Also look for retirement info in list items and paragraphs
        for el in soup.find_all(["li", "p"]):
            text = el.get_text(strip=True)
            series_match = re.search(r"([A-Za-z]+(?:v\d+)?(?:\s+(?:Promo|v\d+))?)\s*[-–]?\s*series", text, re.IGNORECASE)
            if not series_match:
                continue
            retire_date = parse_retirement_date(text)
            if not retire_date:
                continue

            series_name = series_match.group(0).strip()
            family_key = guess_family_key(series_name)
            if family_key not in found:
                link = el.find("a")
                learn_url = link["href"] if link and link.get("href") else PREV_GEN_PAGE
                if learn_url.startswith("/"):
                    learn_url = "https://learn.microsoft.com" + learn_url
                found[family_key] = {
                    "name": series_name,
                    "retireDate": retire_date,
                    "learnMoreUrl": learn_url,
                }

        print(f"[OK] Found {len(found)} retirement entries from main page")

    except Exception as e:
        print(f"[WARN] Failed to fetch/parse retirement page: {e}")

    # --- Parse previous generation page ---
    print(f"[INFO] Fetching {PREV_GEN_PAGE}")
    try:
        resp = requests.get(PREV_GEN_PAGE, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for el in soup.find_all(["li", "p", "td"]):
            text = el.get_text(strip=True)
            series_match = re.search(r"([A-Za-z]+(?:v\d+)?(?:\s+(?:Promo|v\d+))?)\s*[-–]?\s*series", text, re.IGNORECASE)
            if not series_match:
                continue
            retire_date = parse_retirement_date(text)
            if not retire_date:
                continue

            series_name = series_match.group(0).strip()
            family_key = guess_family_key(series_name)
            if family_key not in found:
                found[family_key] = {
                    "name": series_name,
                    "retireDate": retire_date,
                    "learnMoreUrl": PREV_GEN_PAGE,
                }

        print(f"[OK] Total entries after previous-gen page: {len(found)}")

    except Exception as e:
        print(f"[WARN] Failed to fetch/parse previous-gen page: {e}")

    return found


def merge_retirements(existing_data, scraped):
    """Merge scraped data into existing, preserving entries. Returns (data, added, updated)."""
    existing_map = {r["family"]: r for r in existing_data.get("retirements", [])}
    added = []
    updated = []

    for family_key, info in scraped.items():
        if family_key in existing_map:
            old = existing_map[family_key]
            if old.get("retireDate") != info["retireDate"]:
                old["retireDate"] = info["retireDate"]
                updated.append(family_key)
            if old.get("name") != info["name"]:
                old["name"] = info["name"]
                if family_key not in updated:
                    updated.append(family_key)
        else:
            existing_map[family_key] = {
                "family": family_key,
                "name": info["name"],
                "retireDate": info["retireDate"],
                "learnMoreUrl": info.get("learnMoreUrl", PREV_GEN_PAGE),
            }
            added.append(family_key)

    existing_data["retirements"] = list(existing_map.values())
    return existing_data, added, updated


def main():
    print("=" * 60)
    print("VM SKU Retirement Data Updater")
    print("=" * 60)

    existing = load_existing()
    print(f"[INFO] Existing entries: {len(existing.get('retirements', []))}")

    scraped = fetch_and_parse()

    if not scraped:
        print("[WARN] No retirement data scraped. Keeping existing data unchanged.")
        sys.exit(0)

    merged, added, updated = merge_retirements(existing, scraped)

    if added or updated:
        save_data(merged)
        print(f"\n[SUMMARY]")
        print(f"  Added:   {len(added)} entries")
        for a in added:
            print(f"    + {a}")
        print(f"  Updated: {len(updated)} entries")
        for u in updated:
            print(f"    ~ {u}")
        print(f"  Total:   {len(merged['retirements'])} entries")
        print(f"[OK] data/retirements.json updated.")
    else:
        # Still update the timestamp to show we checked
        save_data(merged)
        print(f"\n[OK] No new retirements found. {len(merged['retirements'])} entries unchanged.")


if __name__ == "__main__":
    main()
