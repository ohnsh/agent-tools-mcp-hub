import fs from 'node:fs'
import { makeCoinMarketCapTool, type Asset } from './tool/tool.js'

// if invoked with `npm run start`, the current directory will be the project root.
if (fs.existsSync('.env')) {
  process.loadEnvFile('.env')
}

const { runTool } = makeCoinMarketCapTool()

export const formatAsset = (data: Asset) => {
  const { name, slug, symbol, quote } = data

  const currencyFmt = (() => {
    const opts: Intl.NumberFormatOptions = {
      currency: quote.symbol,
      style: 'currency',
      notation: 'compact',
      maximumSignificantDigits: 4,
    }
    try {
      return new Intl.NumberFormat([], opts)
    } catch {
      return new Intl.NumberFormat([], {
        ...opts,
        currency: 'USD',
      })
    }
  })()

  const percentFmt = new Intl.NumberFormat([], {
    style: 'percent',
    maximumSignificantDigits: 4,
    maximumFractionDigits: 3,
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
    percentKeys.map((key) => [key, percentFmt.format(data.quote[key] / 100)]),
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

// see `npm run demo`. Alternatively, could guard with `if (import.meta.main)` to only run
// when the script is executed directly (other tools here use a similar technique with the
// commonjs `require.main` API).
export async function demoTool() {
  await runTool({ action: 'listCurrencies' }).then(console.log)

  await runTool({
    action: 'rankAssets',
    rankBy: 'percent_change_24h',
  }).then((results) => {
    if (results.success) {
      console.log({ ...results, data: results.data.map(formatAsset) })
    } else {
      console.error(results)
    }
  })
}

export async function dumpTool() {
  const result = await runTool({
    action: 'dumpAssets',
    limit: 5,
  })

  if (result.success) {
    const description = 'Successful assets fetch'
    const output = {
      description,
      response: result.plainResponse,
      apiStatus: result.apiStatus,
      data: result.data,
    }
    process.stdout.write(JSON.stringify(output, undefined, 2))
  }
}
