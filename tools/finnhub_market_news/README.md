# Finnhub Market News & Earnings Calendar Tool

A Python tool that fetches company-specific financial news, general market news, and upcoming earnings announcement dates via the [Finnhub](https://finnhub.io/) Stock API.

## Prerequisites

A free Finnhub API key is required. Register at [finnhub.io/register](https://finnhub.io/register) and either:

- Set it as the `FINNHUB_API_KEY` environment variable, or
- Pass it as the `api_key` parameter.

## Parameters

| Parameter | Type | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `category` | `string` | No | News category: `general`, `forex`, `crypto`, or `earnings` (upcoming earnings calendar) | `general` |
| `symbol` | `string` | No | Company symbol (e.g. `AAPL`). When set, fetches company-specific news | — |
| `limit` | `integer` | No | Number of news items to return | `10` |
| `api_key` | `string` | No | API key; falls back to `FINNHUB_API_KEY` env var | — |

## Usage

```python
import os
from tool import run_tool

os.environ["FINNHUB_API_KEY"] = "your_key_here"

# General market news
news = run_tool(category="general", limit=5)
for item in news["items"]:
    print(f"[{item['source']}] {item['headline']}")

# Company-specific news
aapl = run_tool(symbol="AAPL", limit=5)

# Upcoming earnings calendar
earnings = run_tool(category="earnings", limit=10)
```

### CLI test

```bash
FINNHUB_API_KEY=your_key_here python tool.py
```
