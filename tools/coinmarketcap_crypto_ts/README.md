# CoinMarketCap Top Crypto & Market Cap Explorer (TypeScript)

Fetches current TVL, 24-hour change, chain distribution, and the ten largest yield pools for a DeFi protocol or chain through the free DefiLlama REST API.

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `limit` | `number` | No |  |
| `currency` | `string` | No |  |
| `rankBy` | `string` | No |  |

## Installation and usage

```bash
cd tools/coinmarketcap_crypto_ts
npm install
npm start
# or CMC_API_KEY=KEY npm start
```

The tool needs no API key. Returns...
