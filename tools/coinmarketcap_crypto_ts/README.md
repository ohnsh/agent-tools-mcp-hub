# CoinMarketCap Top Crypto & Market Cap Explorer (TypeScript)

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

## Parameters

*All parameters are optional:*

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `action`   | `'rankAssets' \| 'listCurrencies'` | `'rankAssets'` | The action to run |
| `limit`    | `number` | 10  | Number of assets to fetch from CoinMarketCap |
| `currency` | `string` | USD | Currency in which to display results |
| `rankBy`   | `SortKey` (see below) | `'market_cap'` | Rank assets by this metric |

Valid values for `rankBy`:

```ts
type SortKey =
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

## Return types

On success:
- `runTool({ action: 'rankAssets' })` returns `SuccessResult<Asset[]>`
- `runTool({ action: 'listCurrencies' })` returns `SuccessResult<Fiat[]>`

On error, `runTool` always returns an `ErrorResult` (it does not throw).

```ts
type SuccessResult<T> = {
  success: true
  data: T
  apiStatus?: APIStatus
}
type ErrorResult = {
  success: false
  error: string | { name: string; message: string; details?: Record<string, any> }
}

// Timestamps are ISO UTC (2026-09-02T05:49:00.000Z)
type Timestamp = string

interface Fiat {
  name: string
  sign: string
  symbol: string
}

interface Asset {
  tags: string[]
  id: number
  name: string
  symbol: string
  slug: string
  date_added: Timestamp
  last_updated: Timestamp
  quote: Quote[]
}

interface Quote {
  id: number
  symbol: string
  price: number
  volume_24h: number
  volume_change_24h: number
  cex_volume_24h: number
  dex_volume_24h: number
  percent_change_1h: number
  percent_change_24h: number
  percent_change_7d: number
  percent_change_30d: number
  percent_change_60d: number
  percent_change_90d: number
  market_cap: number
  market_cap_dominance: number
  fully_diluted_market_cap: number
  minted_market_cap: number
  last_updated: Timestamp
}
```
