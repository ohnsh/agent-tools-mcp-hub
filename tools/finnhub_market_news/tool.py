"""
Finnhub Market News & Earnings Calendar Tool

Fetches company-specific financial news and upcoming earnings
announcement dates via the Finnhub Stock API.

Requires a free API key: https://finnhub.io/register
The key can be passed via the `api_key` parameter or the
FINNHUB_API_KEY environment variable.
"""
import json
import os
import urllib.request
import urllib.parse
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

API_URL = "https://finnhub.io/api/v1"


def _get_json(path: str, params: Dict[str, str], timeout: int = 15) -> Optional[Any]:
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(
        f"{API_URL}{path}?{query}",
        headers={"User-Agent": "Mozilla/5.0 (AgentToolsHub/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def run_tool(
    category: str = "general",
    symbol: str = "",
    limit: int = 10,
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Fetch market news or upcoming earnings dates from Finnhub.

    Args:
        category: News category (general, forex, crypto) — used when symbol
            is empty. Set to "earnings" to fetch upcoming earnings calendar.
        symbol: Company symbol (e.g. AAPL). When set, fetches company news.
        limit: Number of news items to return.
        api_key: Finnhub API key; falls back to the FINNHUB_API_KEY
            environment variable.

    Returns:
        Dict with success flag and news/earnings items.
    """
    key = (api_key or os.getenv("FINNHUB_API_KEY") or "").strip()
    if not key:
        return {
            "success": False,
            "error": (
                "Finnhub API key is required. Pass api_key or set the "
                "FINNHUB_API_KEY environment variable (https://finnhub.io/register)."
            )
        }

    try:
        lim = int(limit)
    except (TypeError, ValueError):
        return {"success": False, "error": "limit must be an integer."}
    lim = max(1, min(lim, 100))

    cat = category.strip().lower()
    sym = symbol.strip().upper()

    if cat == "earnings":
        today = date.today()
        week_later = today + timedelta(days=7)
        data = _get_json(
            "/calendar/earnings",
            {
                "from": today.isoformat(),
                "to": week_later.isoformat(),
                "token": key,
            },
        )
        if data is None:
            return {"success": False, "error": "Failed to fetch earnings calendar from Finnhub."}
        earnings = data.get("earningsCalendar", [])
        if not earnings:
            return {"success": True, "category": "earnings", "items": []}
        items = [
            {
                "symbol": e.get("symbol"),
                "date": e.get("date"),
                "hour": e.get("hour"),
                "eps_estimate": e.get("epsEstimate"),
                "revenue_estimate": e.get("revenueEstimate"),
            }
            for e in earnings[:lim]
        ]
        return {"success": True, "category": "earnings", "items": items}

    if sym:
        today = date.today()
        week_ago = today - timedelta(days=7)
        data = _get_json(
            "/company-news",
            {
                "symbol": sym,
                "from": week_ago.isoformat(),
                "to": today.isoformat(),
                "token": key,
            },
        )
        if data is None:
            return {"success": False, "error": f"Failed to fetch news for '{sym}' from Finnhub."}
        if not isinstance(data, list):
            return {"success": False, "error": "Unexpected response from Finnhub."}
        items = [
            {
                "category": n.get("category"),
                "headline": n.get("headline"),
                "summary": n.get("summary"),
                "source": n.get("source"),
                "url": n.get("url"),
                "datetime": n.get("datetime"),
            }
            for n in data[:lim]
        ]
        return {"success": True, "symbol": sym, "items": items}

    if cat not in ("general", "forex", "crypto"):
        return {
            "success": False,
            "error": (
                f"Invalid category '{cat}'. Use 'general', 'forex', 'crypto', "
                "'earnings', or pass a company symbol."
            )
        }

    data = _get_json(
        "/news",
        {"category": cat, "token": key},
    )
    if data is None:
        return {"success": False, "error": f"Failed to fetch {cat} news from Finnhub."}
    if not isinstance(data, list):
        return {"success": False, "error": "Unexpected response from Finnhub."}
    items = [
        {
            "category": n.get("category"),
            "headline": n.get("headline"),
            "summary": n.get("summary"),
            "source": n.get("source"),
            "url": n.get("url"),
            "datetime": n.get("datetime"),
        }
        for n in data[:lim]
    ]
    return {"success": True, "category": cat, "items": items}


if __name__ == "__main__":
    print(json.dumps(run_tool("general", limit=3), indent=2))
