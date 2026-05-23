# btc-statistics — monorepo

Two standalone price-dashboard apps in sibling directories. Each app is fully self-contained: one Python script, one or two CSV data files, one HTML template, one generated output file.

## Structure

```
btc-statistics/
├── strc/                       # STRC (Strategy Preferred Stock) dashboard
│   ├── fetch_strc.py           # fetches data, writes CSV, injects CSV into HTML
│   ├── strc_prices.csv         # persisted daily OHLCV data
│   ├── strc_stats.html         # HTML template (contains DATE_PLACEHOLDER)
│   └── strc_stats_out.html     # generated output — open this in a browser
│
├── bitcoin/                    # Bitcoin (BTC-USD) dashboard
│   ├── fetch_bitcoin.py        # fetches data, writes CSV, injects CSV into HTML
│   ├── bitcoin_prices.csv      # live/recent OHLCV data (created on first run)
│   ├── btc-historical.csv      # optional seed file: full history since 2012
│   ├── bitcoin_stats.html      # HTML template (contains DATE_PLACEHOLDER)
│   └── bitcoin_stats_out.html  # generated output — open this in a browser
│
├── README.md
├── LICENSE
└── CLAUDE.md
```

## How to run

Each app runs independently from its own directory:

```bash
# STRC dashboard
cd strc
python fetch_strc.py

# Bitcoin dashboard
cd bitcoin
python fetch_bitcoin.py
```

Both scripts:
1. Load existing CSV data (skip if already up to date)
2. Fetch new data from the respective API
3. Append new rows to the CSV
4. Inject the full CSV into the HTML template at `DATE_PLACEHOLDER`
5. Write the output HTML and open it in the default browser

## Data sources

| App     | Source                  | Notes                                    |
|---------|-------------------------|------------------------------------------|
| strc    | Yahoo Finance v8 API    | No key required; uses `urllib` only      |
| bitcoin | CoinGecko public API    | No key required; uses `/market_chart?days=365&interval=daily`; free tier cap is 365 days history; `open/high/low` are set equal to `close` (true OHLC beyond 90 days requires a paid key); if `btc-historical.csv` is present it is loaded first as a seed for full history since 2012 |

## Dependencies

- Python 3.10+ (uses `int | str` union type hint)
- Standard library only — no `pip install` needed for either app

## HTML template convention

The template files use the literal string `DATE_PLACEHOLDER` as the injection point for CSV data. The Python scripts replace this with the full CSV content (header + rows) as a JavaScript template literal inside a `<script>` block. All chart rendering is done in vanilla JS with the Canvas API — no external libraries.

## Accent colors

- STRC: `#818cf8` (indigo)
- Bitcoin: `#f7931a` (Bitcoin orange)
