"""
SEC EDGAR Filings Search Tool

Searches SEC EDGAR for public company regulatory filings (10-K, 10-Q,
8-K, ...) by stock ticker or CIK. Uses the official SEC JSON APIs.

Per SEC guidelines, all requests must include a descriptive User-Agent
with contact information: https://www.sec.gov/os/accessing-edgar-data
"""
import json
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

SEC_HEADERS = {
    "User-Agent": "AgentToolsHub/1.0 tool-user@example.com",
}

TICKER_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"

# 10-K and 10-Q have multiple variants (e.g. 10-K/A)
FORM_VARIANTS = {
    "10-K": ["10-K", "10-K/A"],
    "10-Q": ["10-Q", "10-Q/A"],
    "8-K": ["8-K", "8-K/A"],
}


def _get_json(url: str, timeout: int = 15) -> Optional[Dict[str, Any]]:
    req = urllib.request.Request(url, headers=SEC_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return None


def _ticker_to_cik(ticker: str) -> Optional[str]:
    """Resolve a stock ticker to a zero-padded 10-digit CIK."""
    data = _get_json(TICKER_URL)
    if not data:
        return None
    target = ticker.strip().upper()
    for entry in data.values():
        if entry.get("ticker", "").upper() == target:
            return str(entry["cik_str"]).zfill(10)
    return None


def _accession_url(accession: str) -> str:
    """Build a direct filing landing URL from an accession number."""
    clean = accession.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{clean[0:10]}/{clean}/"


def run_tool(
    ticker: str = "AAPL",
    form_type: str = "10-K",
    limit: int = 5,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Search SEC EDGAR for a company's recent filings.

    Args:
        ticker: Stock ticker (e.g. AAPL, MSFT) or 10-digit CIK.
        form_type: Filing form type (10-K, 10-Q, 8-K).
        limit: Number of filings to return (default 5).

    Returns:
        Dict with company info and recent matching filings.
    """
    if not ticker or not ticker.strip():
        return {"success": False, "error": "ticker parameter cannot be empty."}

    try:
        lim = int(limit)
    except (TypeError, ValueError):
        return {"success": False, "error": "limit must be an integer."}
    lim = max(1, min(lim, 100))

    raw = ticker.strip()
    if raw.isdigit() and len(raw) <= 10:
        cik = raw.zfill(10)
        company_name = None
    else:
        cik = _ticker_to_cik(raw)
        company_name = raw.upper()
        if not cik:
            return {"success": False, "error": f"Ticker '{raw}' not found in SEC EDGAR."}

    submissions = _get_json(SUBMISSIONS_URL.format(cik=cik))
    if not submissions:
        return {"success": False, "error": f"Failed to fetch SEC filings for '{raw}'."}

    company_name = submissions.get("name") or company_name
    variants = FORM_VARIANTS.get(form_type.strip().upper(), [form_type.strip().upper()])
    recent = submissions.get("filings", {}).get("recent", {})

    filings = []
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    periods = recent.get("reportDate", [])
    accessions = recent.get("accessionNumber", [])

    for i, form in enumerate(forms):
        if form in variants:
            filings.append(
                {
                    "form_type": form,
                    "filing_date": dates[i] if i < len(dates) else None,
                    "report_period": periods[i] if i < len(periods) else None,
                    "accession_number": accessions[i] if i < len(accessions) else None,
                    "url": _accession_url(accessions[i]) if i < len(accessions) else None,
                }
            )
        if len(filings) >= lim:
            break

    if not filings:
        return {
            "success": False,
            "error": f"No {form_type} filings found for {company_name}.",
        }

    return {
        "success": True,
        "ticker": raw.upper(),
        "cik": cik,
        "company_name": company_name,
        "form_type": form_type,
        "filings": filings,
    }


if __name__ == "__main__":
    result = run_tool("AAPL", "10-K", limit=3)
    print(json.dumps(result, indent=2))
