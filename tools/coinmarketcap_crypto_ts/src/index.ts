import fs from 'node:fs'
import type { APISuccess, Data, Datum, SortKey } from './types.ts'

if (fs.existsSync('.env')) {
  process.loadEnvFile('.env')
}

const CMC_API_KEY = process.env.CMC_API_KEY
const BASE_URL = CMC_API_KEY
  ? 'https://pro-api.coinmarketcap.com'
  : 'https://pro-api.coinmarketcap.com/public-api'
const HEADERS: Record<string, string> = {
  Accept: 'application/json',
  'Accept-Encoding': 'deflate, gzip',
}
if (CMC_API_KEY) {
  Object.assign(HEADERS, { 'X-CMC_PRO_API_KEY': CMC_API_KEY })
}

async function _fetch(path: string) {
  const res = await fetch(`${BASE_URL}${path}`, { headers: HEADERS })
  const json = await res.json()

  if (res.status === 429) {
    /* exceeding rate limit; try backing off */
  }

  if (!res.ok) {
    throw new Error(JSON.stringify(json))
  }

  return json
}

// without an API key, querying more than one currency returns an error:
// 'Your plan is limited to 1 convert options'
export interface ToolOpts {
  limit?: number // default 10, max 100
  currency?: string // 'USD,EUR,BTC,...'
  rank?: SortKey
}

// top {limit} cryptocurrencies by {sort} (default market_cap)
async function getListing(opts: ToolOpts = {}): Promise<Data[]> {
  const { limit = 10, currency, rank } = opts
  const params = new URLSearchParams({
    limit: limit.toString(),
  })
  if (currency) {
    params.set('convert', currency)
  }

  const result = (await _fetch(
    `/v3/cryptocurrency/listings/latest?${params}`,
  )) as APISuccess

  if (rank) {
    result.data.sort((a, b) => {
      switch (rank) {
        case 'name':
        case 'symbol':
          return a[rank].localeCompare(b[rank])
        default:
          // descending sort
          return (b.quote[0]?.[rank] ?? 0) - (a.quote[0]?.[rank] ?? 0)
      }
    })
  }

  return result.data.map(cleanData)
}

async function getCurrencies() {
  await _fetch('/v1/fiat/map')
}

const cleanData = (rawData: Datum): Data => {
  const { name, slug, symbol, quote: [quote] = [] } = rawData
  if (!quote) {
    throw new Error()
  }
  return {
    name,
    slug,
    symbol,
    quote,
  }
}

export async function runTool(opts?: ToolOpts) {
  if (CMC_API_KEY) {
    console.log(
      'CoinMarketCap API key extracted from environment. API calls will be authenticated.',
    )
  } else {
    console.log(
      'No CoinMarketCap API key found in environment. The keyless API will be used.',
    )
  }
  const listing = await getListing(opts)

  return listing
}

const formatData = (data: Data) => {
  const { name, slug, symbol, quote } = data

  const currencyFmt = new Intl.NumberFormat([], {
    currency: quote.symbol,
    style: 'currency',
    notation: 'compact',
    maximumSignificantDigits: 4,
  })
  const percentFmt = new Intl.NumberFormat([], {
    style: 'percent',
    maximumSignificantDigits: 4,
  })

  const percentKeys = [
    'percent_change_1h',
    'percent_change_24h',
    'percent_change_7d',
    'percent_change_30d',
    'percent_change_60d',
    'percent_change_90d',
  ] as const
  const currencyKeys = ['price', 'market_cap', 'volume_24h'] as const

  type PercentKey = (typeof percentKeys)[number]
  type CurrencyKey = (typeof currencyKeys)[number]

  const percentDict = Object.fromEntries(
    percentKeys.map((key) => [key, percentFmt.format(data.quote[key])]),
  ) as Record<PercentKey, string>
  const currencyDict = Object.fromEntries(
    currencyKeys.map((key) => [key, currencyFmt.format(data.quote[key])]),
  ) as Record<CurrencyKey, string>

  return {
    name,
    slug,
    symbol,
    ...currencyDict,
    ...percentDict,
  }
}

await runTool({ currency: 'EUR', rank: 'percent_change_90d' })
  .then((results) => results.map(formatData))
  .then(console.log)
