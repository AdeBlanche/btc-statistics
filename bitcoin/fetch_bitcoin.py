import csv
import json
import subprocess
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

COIN_ID = "bitcoin"
DATA_FILE = Path("bitcoin_prices.csv")
HISTORICAL_FILE = Path("btc-historical.csv")
HTML_TEMPLATE = Path("bitcoin_stats.html")
HTML_OUT = Path(__file__).parent.parent / "docs" / "bitcoin.html"
FIELDNAMES = ["date", "open", "high", "low", "close", "volume"]

# CoinGecko free public API — no key, max 365 days per call, ~10-15 req/min
MARKET_CHART_URL = (
    "https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    "?vs_currency=usd&days={days}&interval=daily"
)


def load_existing() -> dict[str, dict]:
    existing: dict[str, dict] = {}

    # Seed from historical file first (full history since 2012)
    if HISTORICAL_FILE.exists():
        with HISTORICAL_FILE.open(newline="") as f:
            for row in csv.DictReader(f):
                existing[row["date"]] = row

    # Overlay with any rows already in the live data file
    if DATA_FILE.exists():
        with DATA_FILE.open(newline="") as f:
            for row in csv.DictReader(f):
                existing[row["date"]] = row

    return existing


def needs_update(existing: dict[str, dict]) -> bool:
    if not existing:
        return True
    latest = max(existing.keys())
    today = date.today().isoformat()
    return latest < today


def fetch_market_chart(days: int) -> list[dict]:
    url = MARKET_CHART_URL.format(coin=COIN_ID, days=days)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())

    prices = data.get("prices", [])
    volumes = data.get("total_volumes", [])

    vol_by_date = {}
    for ts_ms, vol in volumes:
        d = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).date().isoformat()
        vol_by_date[d] = int(vol)

    rows = []
    for ts_ms, price in prices:
        d = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).date().isoformat()
        p = round(price, 2)
        rows.append({
            "date":   d,
            "open":   p,
            "high":   p,
            "low":    p,
            "close":  p,
            "volume": vol_by_date.get(d, ""),
        })
    return rows


def save(existing: dict[str, dict], new_rows: list[dict]) -> int:
    added = 0
    for row in new_rows:
        if row["date"] not in existing:
            existing[row["date"]] = row
            added += 1

    sorted_rows = sorted(existing.values(), key=lambda r: r["date"])
    with DATA_FILE.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(sorted_rows)
    return added


def build_html():
    template = HTML_TEMPLATE.read_text(encoding="utf-8")
    csv_content = DATA_FILE.read_text(encoding="utf-8").strip()
    html = template.replace("DATE_PLACEHOLDER", csv_content)
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"Dashboard written to {HTML_OUT}")


def main():
    existing = load_existing()

    if not needs_update(existing):
        print(f"Already up to date. Latest: {max(existing.keys())}")
    else:
        latest = max(existing.keys()) if existing else "2012-01-01"
        days_behind = (date.today() - date.fromisoformat(latest)).days + 2
        days = min(days_behind, 365)
        print(f"Fetching last {days} days from CoinGecko (since {latest})...")
        rows = fetch_market_chart(days)
        added = save(existing, rows)
        existing = load_existing()
        print(f"Added {added} new row(s). Total: {len(existing)} days saved to {DATA_FILE}")

    build_html()

    if sys.platform == "win32":
        subprocess.Popen(["explorer", str(HTML_OUT.resolve())])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(HTML_OUT.resolve())])
    else:
        subprocess.Popen(["xdg-open", str(HTML_OUT.resolve())])


if __name__ == "__main__":
    main()
