import re
import json
import httpx
from bs4 import BeautifulSoup

def get_page(url: str) -> BeautifulSoup:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ph-minimum-wage-api/1.0)"
    }
    response = httpx.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def _parse_amount(text: str) -> float | None:
    if not text:
        return None
    # Normalize common currency markers
    text = text.replace("₱", "").replace("PHP", "").replace("Php", "")
    # Find first numeric value with optional commas and decimals
    m = re.search(r"[0-9]{1,3}(?:[,0-9]*)(?:\.[0-9]+)?", text)
    if not m:
        return None
    num = m.group(0).replace(",", "")
    try:
        return float(num)
    except ValueError:
        return None


def parse_wage_table(soup: BeautifulSoup) -> list[dict]:
    """Return cleaned sector wage entries as list of dicts.

    Each dict has: sector, current_wage, wage_increase, new_wage
    """
    tables = soup.find_all("table")
    results: list[dict] = []

    keywords = ("minimum wage", "minimum wage rate", "non-agriculture", "agriculture")
    for table in tables:
        table_text = table.get_text().lower()
        # Only process tables that look like wage tables
        if not any(k in table_text for k in keywords):
            continue
        rows = table.find_all("tr")
        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if not cells:
                continue

            sector = cells[0]
            # If the first cell is itself an amount (e.g. kasambahay row), skip here
            if _parse_amount(sector) is not None:
                continue
            # Skip long header rows or obvious table headers
            if not sector or sector.strip().upper().startswith("MINIMUM WAGE"):
                continue
            if sector.isupper() and len(sector.split()) > 5:
                continue

            # Extract numeric amounts from the row
            amounts = [a for a in (_parse_amount(c) for c in cells) if a is not None]
            if not amounts:
                continue

            # Heuristic: rows with three amounts are (current, increase, new)
            entry: dict = {"sector": sector}
            if len(amounts) >= 3:
                entry.update({
                    "current_wage": amounts[0],
                    "wage_increase": amounts[1],
                    "new_wage": amounts[2],
                })
                results.append(entry)
            elif len(amounts) == 2:
                # Some tables might show current and new (or current and increase)
                entry.update({
                    "current_wage": amounts[0],
                    "wage_increase": None,
                    "new_wage": amounts[1],
                })
                results.append(entry)
            elif len(amounts) == 1:
                # Single amount rows (e.g., kasambahay) handled elsewhere
                continue

    return results

def parse_kasambahay_table(soup: BeautifulSoup) -> dict | None:
    tables = soup.find_all("table")
    for table in tables:
        text = table.get_text()
        tlow = text.lower()
        # Look specifically for kasambahay keywords or known kasambahay amounts
        if (
            "kasambahay" in tlow
            or "7,000" in text
            or "7000" in text
            or "7,800" in text
            or "7800" in text
        ):
            rows = table.find_all("tr")
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                amounts = [a for a in (_parse_amount(c) for c in cells) if a is not None]
                if len(amounts) >= 2:
                    return {
                        "sector": "Kasambahay",
                        "current_wage": amounts[0],
                        "wage_increase": amounts[1] if len(amounts) > 1 else None,
                        "new_wage": amounts[2] if len(amounts) > 2 else None,
                    }
    return None

if __name__ == "__main__":
    print("Testing NCR scrape...\n")
    soup = get_page("https://nwpc.dole.gov.ph/ncr/")

    wage_rows = parse_wage_table(soup)
    kasambahay = parse_kasambahay_table(soup)

    print("=== CLEAN SECTOR DATA ===")
    print(json.dumps(wage_rows, indent=2))

    print("\n=== KASAMBAHAY ===")
    print(json.dumps(kasambahay, indent=2))
    