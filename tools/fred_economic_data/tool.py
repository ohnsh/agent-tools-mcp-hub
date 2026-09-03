"""
FRED Economic Data Tool

Retrieves key macroeconomic series (Federal Funds Rate, CPI, GDP,
Unemployment Rate, ...) from the Federal Reserve Economic Data (FRED) API.

Requires a free FRED API key: https://fred.stlouisfed.org/docs/api/api_key.html
The key can be passed via the `api_key` parameter or the FRED_API_KEY
environment variable.
"""
import json
import os
import urllib.request
import urllib.parse
from typing import Any, Dict, List, Optional

FRED_BASE = "https://api.stlouisfed.org/fred"


def _get(url: str, timeout: int = 15) -> Optional[Dict[str, Any]]:
    """GET a JSON endpoint and return the parsed payload."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (AgentToolsHub/1.0)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def get_series_meta(series_id: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch series metadata (title, frequency, units, ...)."""
    params = urllib.parse.urlencode(
        {"series_id": series_id, "api_key": api_key, "file_type": "json"}
    )
    data = _get(f"{FRED_BASE}/series?{params}")
    if not data:
        return None
    series = data.get("seriess")
    if not series:
        return None
    return series[0]


def get_observations(series_id: str, api_key: str, limit: int) -> Optional[List[Dict[str, Any]]]:
    """Fetch the most recent observations for a series."""
    params = urllib.parse.urlencode(
        {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "limit": limit,
            "sort_order": "desc",
        }
    )
    data = _get(f"{FRED_BASE}/series/observations?{params}")
    if not data:
        return None
    return data.get("observations")


def run_tool(
    series_id: str = "FEDFUNDS",
    limit: int = 10,
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Retrieve recent observations for a FRED macroeconomic series.

    Args:
        series_id: FRED series ID (e.g. FEDFUNDS, CPIAUCSL, GDP, UNRATE).
        limit: Number of most recent data points to return (default 10).
        api_key: FRED API key; falls back to the FRED_API_KEY env variable.

    Returns:
        Dict with success flag, series metadata and formatted observations.
    """
    key = (api_key or os.getenv("FRED_API_KEY") or "").strip()
    if not key:
        return {
            "success": False,
            "error": "FRED API key is required. Pass api_key or set the FRED_API_KEY environment variable (https://fred.stlouisfed.org/docs/api/api_key.html)."
        }

    sid = series_id.strip().upper()
    if not sid:
        return {"success": False, "error": "series_id parameter cannot be empty."}

    try:
        lim = int(limit)
    except (TypeError, ValueError):
        return {"success": False, "error": "limit must be an integer."}
    lim = max(1, min(lim, 100000))

    meta = get_series_meta(sid, key)
    observations = get_observations(sid, key, lim)

    if observations is None:
        return {
            "success": False,
            "error": (
                f"Failed to fetch series '{sid}'. Verify the series ID and that "
                "your FRED API key is valid."
            )
        }

    points = []
    for obs in observations:
        if obs.get("value") in (".", ""):
            continue
        points.append(
            {
                "date": obs.get("date"),
                "value": obs.get("value"),
            }
        )

    title = meta.get("title", sid) if meta else sid
    frequency = meta.get("frequency", "n/a") if meta else "n/a"
    units = meta.get("units", "n/a") if meta else "n/a"

    return {
        "success": True,
        "series_id": sid,
        "title": title,
        "frequency": frequency,
        "units": units,
        "observations": points,
    }


if __name__ == "__main__":
    result = run_tool("FEDFUNDS", limit=5)
    print(json.dumps(result, indent=2))
