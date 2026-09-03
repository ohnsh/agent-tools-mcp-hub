# FRED Economic Data Tool

A Python tool that retrieves key US macroeconomic series from the Federal Reserve Economic Data (FRED) API — e.g. Federal Funds Rate (`FEDFUNDS`), CPI (`CPIAUCSL`), GDP, and Unemployment Rate (`UNRATE`).

## Prerequisites

A free FRED API key is required. Get one at [fred.stlouisfed.org/docs/api/api_key.html](https://fred.stlouisfed.org/docs/api/api_key.html) and either:

- Set it as the `FRED_API_KEY` environment variable, or
- Pass it as the `api_key` parameter.

## Parameters

| Parameter | Type | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `series_id` | `string` | Yes | FRED series ID (e.g. `FEDFUNDS`, `CPIAUCSL`, `GDP`, `UNRATE`) | `FEDFUNDS` |
| `limit` | `integer` | No | Number of most recent data points to return | `10` |
| `api_key` | `string` | No | FRED API key; falls back to `FRED_API_KEY` env var | — |

## Usage

```python
import os
from tool import run_tool

os.environ["FRED_API_KEY"] = "your_key_here"

result = run_tool(series_id="FEDFUNDS", limit=10)
if result["success"]:
    print(f"Series: {result['title']} ({result['frequency']})")
    for obs in result["observations"]:
        print(f"  {obs['date']}: {obs['value']}")
```

### CLI test

```bash
FRED_API_KEY=your_key_here python tool.py
```

## Useful series IDs

| Series | Description |
| :--- | :--- |
| `FEDFUNDS` | Effective Federal Funds Rate |
| `CPIAUCSL` | Consumer Price Index for All Urban Consumers |
| `GDP` | Gross Domestic Product |
| `UNRATE` | Civilian Unemployment Rate |
| `DGS10` | 10-Year Treasury Constant Maturity Rate |
