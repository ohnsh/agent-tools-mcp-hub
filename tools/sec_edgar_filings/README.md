# SEC EDGAR Filings Search Tool

A zero-auth Python tool that searches SEC EDGAR for public company regulatory filings (10-K, 10-Q, 8-K, ...) by stock ticker or CIK.

## Parameters

| Parameter | Type | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `ticker` | `string` | Yes | Stock ticker (e.g. `AAPL`, `MSFT`) or 10-digit CIK | `AAPL` |
| `form_type` | `string` | No | Filing form type (`10-K`, `10-Q`, `8-K`) | `10-K` |
| `limit` | `integer` | No | Number of filings to return (1-100) | `5` |

## Usage

```python
from tool import run_tool

result = run_tool(ticker="AAPL", form_type="10-Q", limit=3)
if result["success"]:
    print(f"{result['company_name']} recent {result['form_type']} filings:")
    for f in result["filings"]:
        print(f"  {f['filing_date']} ({f['report_period']}): {f['url']}")
```

### CLI test

```bash
python tool.py
```

## Notes

- Uses the official SEC JSON APIs (`company_tickers.json` + company submissions).
- Per [SEC guidelines](https://www.sec.gov/os/accessing-edgar-data), a descriptive User-Agent is set on all requests. For high-volume production use, replace the contact address in `SEC_HEADERS` with your own.
- 10-K and 10-Q searches also match their amendment variants (`10-K/A`, `10-Q/A`).
