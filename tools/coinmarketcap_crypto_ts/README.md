# CoinMarketCap Top Crypto & Market Cap Explorer (TypeScript)



## Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `action` | `'rankAssets' \| 'listCurrencies'` | No | `'rankAssets'` | The action to run
| `limit` | `number` | No | 10 | Number of assets to fetch from CoinMarketCap
| `currency` | `string` | No | USD | Currency in which to display results
| `rankBy` | `SortKey` (see below) | No | `'market_cap'` | Rank assets by this metric

```ts
// valid values for `rankBy` option:
export type SortKey =
  | 'market_cap'
  | 'name'
  | 'symbol'
  | 'price'
  | 'volume_24h'
  | 'percent_change_1h'
  | 'percent_change_24h'
  | 'percent_change_7d'
  | 'percent_change_30d'
  | 'percent_change_60d'
  | 'percent_change_90d'
```

## Installation and usage

### Run the demo

```bash
cd tools/coinmarketcap_crypto_ts
npm install

# if you have a CoinMarketCap API key:
export CMC_API_KEY=KEY

npm run demo
```

### Use from your own project

```bash
# set to the location of this repository's tools directory on your system:
TOOLS_DIR=agent-tools-mcp-hub/tools
npm install "file:$TOOLS_DIR/coinmarketcap_crypto_ts"
```

If you have a CoinMarketCap API key, set `CMC_API_KEY` in your environment. This package will attempt to load a `.env` file in the current directory.

```ts
import { runTool } from 'coinmarketcap-crypto-ts'

const currencyResult = await runTool({ action: 'listCurrencies' })
if (!currencyResult.success) {
  throw currencyResult.error
}

for (const { symbol } of currencyResult.data) {
  // fiat currency symbols that can be passed to `rankAssets` to control output
}

const result = await runTool({
  // limit: 10,
  // currency: 'USD',
  // rankBy: 'market_cap' (see SortKey definition)
})
if (!result.success) {
  throw result.error
}

const { data: assets, apiStatus } = result
// `assets` is an array of crypto assets
// `apiStatus` is a status object returned by the CoinMarketCap API.
for (const asset of assets) {
  // `asset.quote` contains live trading info in the requested currency
}
```
