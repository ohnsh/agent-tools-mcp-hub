# Crypto Fear and Greed Index Tool

A zero-auth Python tool that fetches the daily Crypto Fear and Greed Index from the public [Alternative.me API](https://alternative.me/crypto/fear-and-greed-index/). The index rates market sentiment from 0 (Extreme Fear) to 100 (Extreme Greed).

## Parameters

| Parameter | Type | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `days` | `integer` | No | Number of daily data points to return (1-30) | `7` |

## Usage

```python
from tool import run_tool

result = run_tool(days=7)
if result["success"]:
    print(f"Today: {result['current']['value']} ({result['current']['classification']})")
    for day in result["history"]:
        print(f"  {day['date']}: {day['value']} {day['classification']}")
```

### CLI test

```bash
python tool.py
```

## Classification scale

| Value range | Label |
| :--- | :--- |
| 0-24 | Extreme Fear |
| 25-44 | Fear |
| 45-54 | Neutral |
| 55-74 | Greed |
| 75-100 | Extreme Greed |
