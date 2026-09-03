# Alpha Vantage Stock History & Technical Indicator Tool

A Python tool that fetches historical stock prices (daily OHLCV) or common technical indicators (SMA, RSI, EMA, MACD) via the free [Alpha Vantage](https://www.alphavantage.co/) REST API.

## Prerequisites

A free Alpha Vantage API key is required. Get one at [alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key) and either:

- Set it as the `ALPHA_VANTAGE_API_KEY` environment variable, or
- Pass it as the `api_key` parameter.

## Parameters

| Parameter | Type | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `symbol` | `string` | Yes | Stock symbol (e.g. `AAPL`, `TSLA`) | `AAPL` |
| `function` | `string` | No | `TIME_SERIES_DAILY` or indicator (`SMA`, `RSI`, `EMA`, `MACD`) | `TIME_SERIES_DAILY` |
| `limit` | `integer` | No | Number of most recent data points to return | `10` |
| `api_key` | `string` | No | API key; falls back to `ALPHA_VANTAGE_API_KEY` env var | — |

## Usage

```python
import os
from tool import run_tool

os.environ["ALPHA_VANTAGE_API_KEY"] = "your_key_here"

# Daily OHLCV history
history = run_tool(symbol="AAPL", function="TIME_SERIES_DAILY", limit=5)
for p in history["points"]:
    print(f"{p['date']}: close {p['close']}")

# RSI indicator
rsi = run_tool(symbol="TSLA", function="RSI", limit=5)
for p in rsi["points"]:
    print(f"{p['date']}: RSI {p.get('RSI')}")
```

### CLI test

```bash
ALPHA_VANTAGE_API_KEY=your_key_here python tool.py
```

## Notes

- Free tier supports 25 requests/day; use `outputsize=compact` for daily history to keep responses small.
- Indicator functions return the values keyed by the indicator name (e.g. `RSI`, `SMA`).
