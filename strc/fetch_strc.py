import csv
import json
import subprocess
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

TICKER = "STRC"
DATA_FILE = Path("strc_prices.csv")
HTML_TEMPLATE = Path("strc_stats.html")
HTML_OUT = Path("strc_stats_out.html")
FIELDNAMES = ["date", "open", "high", "low", "close", "volume"]


def load_existing() -> dict[str, dict]:
    if not DATA_FILE.exists():
        return {}
    with DATA_FILE.open(newline="") as f:
        reader = csv.DictReader(f)
        return {row["date"]: row for row in reader}


def needs_update(existing: dict[str, dict]) -> bool:
    if not existing:
        return True
    latest = max(existing.keys())
    today = date.today().isoformat()
    return latest < today


def fetch_yahoo(start_ts: int, end_ts: int) -> list[dict]:
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}"
        f"?interval=1d&period1={start_ts}&period2={end_ts}&events=history"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())

    result = data["chart"]["result"][0]
    timestamps = result["timestamp"]
    quotes = result["indicators"]["quote"][0]

    rows = []
    for i, ts in enumerate(timestamps):
        day = datetime.fromtimestamp(ts, tz=timezone.utc).date().isoformat()
        rows.append({
            "date": day,
            "open":   round(quotes["open"][i], 4)   if quotes["open"][i]   is not None else "",
            "high":   round(quotes["high"][i], 4)   if quotes["high"][i]   is not None else "",
            "low":    round(quotes["low"][i], 4)    if quotes["low"][i]    is not None else "",
            "close":  round(quotes["close"][i], 4)  if quotes["close"][i]  is not None else "",
            "volume": int(quotes["volume"][i])       if quotes["volume"][i] is not None else "",
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
        if existing:
            latest = max(existing.keys())
            start_dt = datetime.fromisoformat(latest).replace(tzinfo=timezone.utc)
            start_ts = int(start_dt.timestamp()) + 86400
            print(f"Fetching new data from {latest} onwards...")
        else:
            start_ts = 0
            print("Fetching full history...")

        end_ts = int(datetime.now(tz=timezone.utc).timestamp()) + 86400
        rows = fetch_yahoo(start_ts, end_ts)
        existing = load_existing()  # reload after save
        added = save(existing, rows)
        existing = load_existing()
        print(f"Added {added} new row(s). Total: {len(existing)} trading days saved to {DATA_FILE}")

    build_html()

    # open in default browser
    if sys.platform == "win32":
        subprocess.Popen(["explorer", str(HTML_OUT.resolve())])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(HTML_OUT.resolve())])
    else:
        subprocess.Popen(["xdg-open", str(HTML_OUT.resolve())])


if __name__ == "__main__":
    main()
