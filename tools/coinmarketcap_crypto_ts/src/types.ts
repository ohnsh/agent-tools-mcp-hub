export type { APISuccess, APIError } from './generated.ts'
import type { Datum, Quote } from './generated.ts'

export interface Data extends Pick<Datum, 'name' | 'slug' | 'symbol'> {
  quote: Quote
}

export type { Quote, Datum }

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
