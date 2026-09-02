// generated with:
//   ENDPOINT="https://pro-api.coinmarketcap.com/public-api/v3/cryptocurrency/listings/latest?limit=10&convert=USD"
//   curl -s "$ENDPOINT" | npx quicktype -l ts

// (runtime helpers removed and several manual edits made)

// ISO UTC (2026-09-02T05:49:00.000Z)
type Timestamp = string

export interface APISuccess {
  data: Datum[]
  status: SuccessStatus
}

export interface APIError {
  status: Status
}

export interface Status {
  timestamp: Timestamp
  error_code: string | number
  error_message: string
  elapsed: number
  credit_count: number
}

interface SuccessStatus extends Status {
  error_code: 0 | '0'
  error_message: ''
}

export interface Datum {
  tags: string[]
  id: number
  name: string
  symbol: string
  slug: string
  infinite_supply: boolean
  circulating_supply: number
  total_supply: number
  max_supply: number | null
  date_added: Timestamp
  num_market_pairs: number
  cmc_rank: number
  last_updated: Timestamp
  tvl_ratio: null
  self_reported_circulating_supply: number | null
  self_reported_market_cap: number | null
  minted_market_cap: number
  quote: Quote[]
}

export interface Quote {
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
  tvl: null
  last_updated: Timestamp
}
