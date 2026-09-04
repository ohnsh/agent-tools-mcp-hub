import fs from 'node:fs'
import type {
  Asset as ApiAsset,
  Quote,
  ListingSuccess,
  FiatMapSuccess,
  SortKey,
  APIError,
  Status as APIStatus,
} from './types.ts'

// if invoked with `npm run start`, the current directory will be the project root.
if (fs.existsSync('.env')) {
  process.loadEnvFile('.env')
}

// ref: https://coinmarketcap.com/api/documentation/pro-api-reference/keyless-public-api
const defaultBaseUrl = (apiKey?: string) => {
  const hardCoded = apiKey
    ? 'https://pro-api.coinmarketcap.com'
    : 'https://pro-api.coinmarketcap.com/public-api'

  return process.env.CMC_BASE_URL || hardCoded
}

// consistent with other tools in agent-tools-mcp-hub
const USER_AGENT =
  'AgentToolsHub/1.0 (https://github.com/tarunjandra/agent-tools-mcp-hub)'

// flattened, simplified version of API type
interface Asset extends Pick<ApiAsset, 'name' | 'slug' | 'symbol'> {
  quote: Quote
}

// without an API key, querying more than one currency returns an error:
// 'Your plan is limited to 1 convert options'
interface ListingOpts {
  limit?: number // default 10, max 100
  currency?: string // 'USD,EUR,BTC,...'
  rankBy?: SortKey
}

interface CmcError {
  name: 'CmcError'
  message: string
  details: Record<string, any>
}

const isCmcError = (err: unknown): err is CmcError =>
  !!err && typeof err === 'object' && 'name' in err && err.name === 'CmcError'

function makeApiClient({
  apiKey = process.env.CMC_API_KEY,
  baseUrl = defaultBaseUrl(apiKey),
}: {
  apiKey?: string
  baseUrl?: string
} = {}) {
  type HeadersInit = NonNullable<ConstructorParameters<typeof Headers>[0]>

  const log = []
  log.push(
    apiKey
      ? 'CoinMarketCap API key extracted from environment. API calls will be authenticated.'
      : 'No CoinMarketCap API key found in environment. The keyless API will be used.',
  )

  // ref: https://coinmarketcap.com/api/documentation/guides/standards-and-conventions
  const buildHeaders = (init?: HeadersInit) => {
    const headers = new Headers(init)
    headers.set('Accept', 'application/json')
    headers.set('Accept-Encoding', 'deflate, gzip')
    headers.set('User-Agent', USER_AGENT)
    if (apiKey) {
      headers.set('X-CMC_PRO_API_KEY', apiKey)
    }

    return headers
  }

  // use typescript function overloads to allow for a plain-response-returning variant
  // while keeping other calls strongly typed. This could also work for `runTool` variants
  // (currently uses a generic to which a parameter is assigned).
  async function cmcFetch(
    url: string | URL,
    init: RequestInit | undefined,
    raw: true,
  ): Promise<Response>

  async function cmcFetch<T>(
    url: string | URL,
    init?: RequestInit,
    raw?: boolean,
  ): Promise<T>

  async function cmcFetch<T>(
    url: string | URL,
    init?: RequestInit,
    raw = false,
  ): Promise<T | Response> {
    const res = await fetch(url, { ...init, headers: buildHeaders(init?.headers) })
    if (raw) {
      return res
    }

    if (res.status === 429) {
      // exceeding rate limit; could implement retry with back-off
    }

    if (!res.ok) {
      const apiError = (await res.json()) as APIError
      const error: CmcError = {
        name: 'CmcError',
        message: apiError.status.error_message,
        details: {
          httpStatus: res.status,
          httpStatusText: res.statusText,
          ...apiError.status,
        },
      }
      throw error
    }

    return res.json() as Promise<T>
  }

  const cleanData = (rawData: ApiAsset): Asset => {
    const [quote] = rawData.quote
    if (!quote) {
      throw new Error('Asset returned by CoinMarketCap API did not contain quote data.')
    }
    return {
      name: rawData.name,
      slug: rawData.slug,
      symbol: rawData.symbol,
      quote,
    }
  }

  interface Fiat {
    name: string
    sign: string
    symbol: string
  }

  const cmcAssetsUrl = (opts: ListingOpts = {}) => {
    const { limit = 10, currency } = opts
    const params = new URLSearchParams({
      limit: limit.toString(),
    })
    if (currency) {
      params.set('convert', currency)
    }
    return `${baseUrl}/v3/cryptocurrency/listings/latest?${params}`
  }

  return {
    // top {limit} cryptocurrencies ranked by {rankBy} (default market_cap)
    async cmcGetAssets(opts: ListingOpts = {}): Promise<SuccessResult<Asset[]>> {
      const { rankBy } = opts
      return cmcFetch<ListingSuccess>(cmcAssetsUrl(opts)).then((r) => {
        const apiStatus = r.status
        const data = r.data.map(cleanData)

        type SortFn = (a: Asset, b: Asset) => number
        let sortFn: SortFn | undefined

        if (rankBy === 'name' || rankBy === 'symbol')
          sortFn = (a, b) => a[rankBy].localeCompare(b[rankBy])
        else if (rankBy) {
          sortFn = (a, b) => b.quote[rankBy] - a.quote[rankBy]
        }
        return {
          success: true,
          data: sortFn ? data.sort(sortFn) : data,
          apiStatus,
        }
      })
    },

    async cmcGetFiatCurrencies(): Promise<SuccessResult<Fiat[]>> {
      const res = await cmcFetch<FiatMapSuccess>(`${baseUrl}/v1/fiat/map?limit=30`)
      const apiStatus = res.status
      const data = res.data.map(({ name, sign, symbol }) => ({ name, sign, symbol }))

      return {
        success: true,
        data,
        apiStatus,
      }
    },

    async cmcDumpAssets(opts: ListingOpts = {}): Promise<SuccessResult<ApiAsset[]>> {
      const response = await cmcFetch(cmcAssetsUrl(opts), undefined, true)

      const plainResponse: PlainResponse = {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        ok: response.ok,
        redirected: response.redirected,
        type: response.type,
        url: response.url,
      }
      const json = (await response.json()) as ListingSuccess

      // returning isn't the point here, but TypeScript is a lot happier if we return a
      // dummy object of the right shape to be a real tool action.
      return {
        success: true,
        plainResponse,
        data: json.data,
        apiStatus: json.status,
      }
    },

    log,
  }
}

const { cmcGetAssets, cmcGetFiatCurrencies, cmcDumpAssets, log } = makeApiClient()

const pureResponseKeys = [
  'status',
  'statusText',
  'ok',
  'redirected',
  'type',
  'url',
] as const

type PureResponseKeys = (typeof pureResponseKeys)[number]
type PlainResponse = {
  [K in PureResponseKeys]: Response[K]
} & {
  headers: Record<string, string>
}

const toolMap = {
  rankAssets: cmcGetAssets,
  listCurrencies: cmcGetFiatCurrencies,
  dumpAssets: cmcDumpAssets,
} as const

export type ToolAction = keyof typeof toolMap
type ToolData<T extends ToolAction> = Awaited<ReturnType<(typeof toolMap)[T]>>['data']

type SuccessResult<T> = {
  success: true
  data: T
  apiStatus: APIStatus
  plainResponse?: PlainResponse
  log?: string[]
}
type ErrorResult = {
  success: false
  error: string | { name: string; message: string; details?: Record<string, any> }
  log?: string[]
}

export interface ToolParams<T extends ToolAction> extends ListingOpts {
  action: T
}

export async function runTool<T extends ToolAction = 'rankAssets'>({
  action = 'rankAssets' as T,
  ...opts
}: ToolParams<T>): Promise<SuccessResult<ToolData<T>> | ErrorResult> {
  try {
    switch (action) {
      case 'rankAssets':
      case 'listCurrencies':
      case 'dumpAssets': {
        const result = await toolMap[action](opts)
        return { ...result, log }
      }

      default: {
        return {
          success: false,
          error: `Unknown action: ${action}. Try 'rankAssets' or 'listCurrencies'.`,
          log,
        }
      }
    }
  } catch (err) {
    if (err instanceof Error) {
      return {
        success: false,
        error: { name: err.name, message: err.message },
        log,
      }
    }
    if (isCmcError(err)) {
      return {
        success: false,
        error: { ...err },
        log,
      }
    }

    // fallback for unrecognized errors
    return {
      success: false,
      error: `${err}`,
      log,
    }
  }
}

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
