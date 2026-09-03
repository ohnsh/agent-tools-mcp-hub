"""
Crypto Fear and Greed Index Tool

Fetches the daily Crypto Fear and Greed Index from the public
Alternative.me API. The index scores market sentiment from 0
(Extreme Fear) to 100 (Extreme Greed).
"""
import json
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

API_URL = "https://api.alternative.me/fng/"

CLASSIFICATIONS = {
    (0, 25): "Extreme Fear",
    (25, 45): "Fear",
    (45, 55): "Neutral",
    (55, 75): "Greed",
    (75, 101): "Extreme Greed",
}


def classify(value: int) -> str:
    """Map a raw 0-100 score to its sentiment label."""
    for (lo, hi), label in CLASSIFICATIONS.items():
        if lo <= value < hi:
            return label
    return "Neutral"


def _fetch(days: int) -> Optional[List[Dict[str, Any]]]:
    url = f"{API_URL}?limit={days}&format=json"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (AgentToolsHub/1.0)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return payload.get("data") or []
    except Exception:
        return None


def run_tool(days: int = 7, **kwargs: Any) -> Dict[str, Any]:
    """
    Fetch the Crypto Fear and Greed Index for the last N days.

    Args:
        days: Number of daily data points to return (1-30, default 7).

    Returns:
        Dict with current sentiment score/classification and history.
    """
    try:
        d = int(days)
    except (TypeError, ValueError):
        return {"success": False, "error": "days must be an integer."}
    d = max(1, min(d, 30))

    data = _fetch(d)
    if data is None:
        return {
            "success": False,
            "error": "Failed to fetch Fear and Greed Index from Alternative.me API."
        }
    if not data:
        return {"success": False, "error": "API returned no data."}

    history = []
    for entry in data:
        try:
            ts = int(entry.get("timestamp", 0))
            date = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        except (TypeError, ValueError, OSError):
            date = entry.get("timestamp", "unknown")
        value = int(entry.get("value", 0))
        history.append(
            {
                "date": date,
                "value": value,
                "classification": classify(value),
            }
        )

    current = history[0]
    return {
        "success": True,
        "current": {
            "value": current["value"],
            "classification": current["classification"],
            "date": current["date"],
        },
        "history": history,
    }


if __name__ == "__main__":
    result = run_tool(days=7)
    print(json.dumps(result, indent=2))
