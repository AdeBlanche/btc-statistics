# btc-statistics

Local price dashboards for Bitcoin (BTC-USD) and STRC (Strategy Preferred Stock). Each dashboard fetches daily OHLCV data, appends it to a local CSV, and generates a standalone HTML file with interactive charts — no server, no dependencies, no API keys.

## Dashboards

| Dashboard | Ticker | Data source | History |
|-----------|--------|-------------|---------|
| Bitcoin   | BTC-USD | CoinGecko public API | Up to 365 days (free tier); full history from 2012 with optional seed file |
| STRC      | STRC    | Yahoo Finance v8 API | Full history from first available trading day |

## Requirements

- Python 3.10+
- No third-party packages — standard library only (`urllib`, `csv`, `json`, `subprocess`)

## Usage

Run each dashboard from its own directory:

```bash
# Bitcoin
cd bitcoin
python fetch_bitcoin.py

# STRC
cd strc
python fetch_strc.py
```

Each script:
1. Loads any existing CSV data
2. Skips the fetch if data is already current
3. Fetches only the missing days from the API
4. Appends new rows to the CSV
5. Injects the full CSV into the HTML template and writes the output file
6. Opens the dashboard in your default browser

## Bitcoin: extending history beyond 365 days

The CoinGecko free tier caps requests at 365 days. To load the full price history back to 2012, place a `btc-historical.csv` file (same `date,open,high,low,close,volume` format) inside the `bitcoin/` directory before running the script. The script loads it as a seed and overlays newer live data on top.

> Note: CoinGecko's free API only returns a single close price per day — `open`, `high`, and `low` are set equal to `close`. True intraday OHLC beyond 90 days requires a paid API key.

## Project structure

```
btc-statistics/
├── bitcoin/
│   ├── fetch_bitcoin.py        # fetch + generate
│   ├── bitcoin_prices.csv      # persisted live data
│   ├── btc-historical.csv      # optional historical seed (not tracked by git)
│   ├── bitcoin_stats.html      # chart template
│   └── bitcoin_stats_out.html  # generated output — open in browser
└── strc/
    ├── fetch_strc.py           # fetch + generate
    ├── strc_prices.csv         # persisted data
    ├── strc_stats.html         # chart template
    └── strc_stats_out.html     # generated output — open in browser
```

## How it works

The HTML templates contain a `DATE_PLACEHOLDER` marker. The Python scripts replace it with the full CSV content as a JavaScript template literal, producing a self-contained HTML file with all data embedded inline. Charts are rendered with the Canvas API — no charting libraries required.
