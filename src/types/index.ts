/**
 * Tesla tracking data types
 *
 * NOTE: These types are now generated from the Zod schema in schema.ts
 * The schema is the single source of truth for validation.
 *
 * If you need to add/modify types, update schema.ts first.
 */

// Re-export types from schema
export type {
  TeslaData,
} from '../schema'

// Legacy exports for backward compatibility
// These are inferred from the Zod schema
import type { TeslaData } from '../schema'

export type WeeklySummary = TeslaData['weeklySummaries'][number]
export type KeyChange = WeeklySummary['keyChanges'][number]
export type QuarterlyData = TeslaData['categories']['productionDelivery']['quarterlyData'][number]
export type AnnualSummary = TeslaData['categories']['productionDelivery']['annualSummary'][number]
export type ProductionDeliveryCategory = TeslaData['categories']['productionDelivery']
export type MetricDataPoint = TeslaData['metrics']['cybercab']['data'][number]
export type RobotaxiCity = TeslaData['metrics']['robotaxiCities']['cities'][number]
export type Metrics = TeslaData['metrics']
export type Category = TeslaData['categories']['aiChip']
