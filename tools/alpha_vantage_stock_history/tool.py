"""
Alpha Vantage Stock History & Technical Indicator Tool

Fetches historical stock prices (daily OHLCV) or common technical
indicators (SMA, RSI) via the free Alpha Vantage REST API.

Requires a free API key: https://www.alphavantage.co/support/#api-key
The key can be passed via the `api_key` parameter or the
ALPHA_VANTAGE_API_KEY environment variable.
"""
import json
import os
import urllib.request
import urllib.parse
from typing import Any, Dict, List, Optional

API_URL = "https://www.alphavantage.co/query"


def _get_json(params: Dict[str, str], timeout: int = 15) -> Optional[Dict[str, Any]]:
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(
        f"{API_URL}?{query}",
        headers={"User-Agent": "Mozilla/5.0 (AgentToolsHub/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _parse_daily(data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
    series = data.get("Time Series (Daily)", {})
    points = []
    for date, values in sorted(series.items(), reverse=True):
        points.append(
            {
                "date": date,
                "open": values.get("1. open"),
                "high": values.get("2. high"),
                "low": values.get("3. low"),
                "close": values.get("4. close"),
                "volume": values.get("5. volume"),
            }
        )
        if len(points) >= limit:
            break
    return points


def _parse_indicator(data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
    # Technical indicator endpoints return a single key like "Technical Analysis: SMA"
    points = []
    for key, series in data.items():
        if not key.startswith("Technical Analysis:"):
            continue
        for date, values in sorted(series.items(), reverse=True):
            entry = {"date": date}
            entry.update(values)
            points.append(entry)
        break
    return points[:limit]


def run_tool(
    symbol: str = "AAPL",
    function: str = "TIME_SERIES_DAILY",
    limit: int = 10,
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Fetch historical stock data or technical indicators from Alpha Vantage.

    Args:
        symbol: Stock symbol (e.g. AAPL, TSLA).
        function: API function. TIME_SERIES_DAILY for OHLCV history,
            or an indicator function (SMA, RSI, EMA, MACD, ...).
        limit: Number of most recent data points to return.
        api_key: Alpha Vantage API key; falls back to the
            ALPHA_VANTAGE_API_KEY environment variable.

    Returns:
        Dict with success flag and parsed data points.
    """
    key = (api_key or os.getenv("ALPHA_VANTAGE_API_KEY") or "").strip()
    if not key:
        return {
            "success": False,
            "error": (
                "Alpha Vantage API key is required. Pass api_key or set the "
                "ALPHA_VANTAGE_API_KEY environment variable "
                "(https://www.alphavantage.co/support/#api-key)."
            )
        }

    sym = symbol.strip().upper()
    if not sym:
        return {"success": False, "error": "symbol parameter cannot be empty."}

    func = function.strip().upper()
    if not func:
        return {"success": False, "error": "function parameter cannot be empty."}

    try:
        lim = int(limit)
    except (TypeError, ValueError):
        return {"success": False, "error": "limit must be an integer."}
    lim = max(1, min(lim, 1000))

    params = {
        "function": func,
        "symbol": sym,
        "apikey": key,
    }
    if func == "TIME_SERIES_DAILY":
        params["outputsize"] = "compact"

    data = _get_json(params)
    if data is None:
        return {
            "success": False,
            "error": f"Failed to fetch data from Alpha Vantage for '{sym}' ({func})."
        }

    if "Information" in data or "Note" in data or "Error Message" in data:
        return {
            "success": False,
            "error": data.get("Information") or data.get("Note") or data.get("Error Message"),
        }

    if func == "TIME_SERIES_DAILY":
        points = _parse_daily(data, lim)
        meta = data.get("Meta Data", {})
        return {
            "success": True,
            "symbol": sym,
            "function": func,
            "last_refreshed": meta.get("3. Last Refreshed"),
            "points": points,
        }

    points = _parse_indicator(data, lim)
    if not points:
        return {
            "success": False,
            "error": f"No data returned for function '{func}'. Verify the function name (e.g. SMA, RSI)."
        }
    return {
        "success": True,
        "symbol": sym,
        "function": func,
        "points": points,
    }


if __name__ == "__main__":
    # Demo requires a real key; print the no-key guidance for CLI users.
    print(json.dumps(run_tool("AAPL", "TIME_SERIES_DAILY", 5), indent=2))
