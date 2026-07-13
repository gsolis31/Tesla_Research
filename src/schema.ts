/**
 * Zod schema for Tesla tracking data
 * This is the single source of truth for data validation
 */

import { z } from 'zod'

// Status enums
const StatusEnum = z.enum(['positive', 'negative', 'neutral'])
const ConfidenceEnum = z.enum(['high', 'medium', 'low'])
const CityStatusEnum = z.enum(['active', 'mapped'])
const ServiceTypeEnum = z.enum(['unsupervised', 'mixed', 'safety-monitor-only'])

// Weekly Summary schemas
const SentimentSchema = z.object({
  headline: z.string(),
  reality: z.string(),
  confidence: ConfidenceEnum,
  rationale: z.string().optional(),
})

const EvidenceSchema = z.object({
  positive_signals: z.array(z.string()),
  negative_signals: z.array(z.string()),
  key_metrics: z.object({
    actual: z.union([z.string(), z.number()]), // Can be string or number
    target: z.string(),
    trajectory: z.string(),
  }).optional(),
})

const KeyChangeSchema = z.object({
  status: StatusEnum,
  sentiment: SentimentSchema.optional(),
  evidence: EvidenceSchema.optional(),
  category: z.string(),
  title: z.string().max(120, 'Title must be under 120 characters'),
  description: z.string(),
  source: z.string().url('Source must be a valid URL'),
})

const WeeklySummarySchema = z.object({
  weekOf: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Must be YYYY-MM-DD format'),
  keyChanges: z.array(KeyChangeSchema),
  trends: z.array(z.string()),
})

// Metric schemas
const MetricDataPointSchema = z.object({
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Must be YYYY-MM-DD format'),
  count: z.number().int().nonnegative(),
  note: z.string(),
})

const RobotaxiCitySchema = z.object({
  name: z.string(),
  status: CityStatusEnum,
  serviceType: ServiceTypeEnum,
  vehicleType: z.string(),
  activeVehicles: z.number().int().nonnegative().nullable(), // Can be null
  breakdown: z.object({
    unsupervised: z.number().int().nonnegative(),
    safetyMonitor: z.number().int().nonnegative(),
    cybercabTesting: z.number().int().nonnegative().optional(),
  }).optional(),
  launchDate: z.string().nullable(),
  serviceArea: z.string(),
  notes: z.string(),
})

const MetricsSchema = z.object({
  cybercab: z.object({
    title: z.string(),
    data: z.array(MetricDataPointSchema),
  }),
  robotaxiFleet: z.object({
    title: z.string(),
    data: z.array(MetricDataPointSchema),
    target: z.string(),
    breakdown: z.object({
      active: z.number().int().nonnegative(),
      staged: z.number().int().nonnegative(),
      cities: z.array(z.string()),
    }),
  }),
  robotaxiCities: z.object({
    title: z.string(),
    lastUpdated: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    cities: z.array(RobotaxiCitySchema),
    summary: z.object({
      totalCities: z.number().int().nonnegative(),
      activeCities: z.number().int().nonnegative(),
      mappedOnly: z.number().int().nonnegative(),
      unsupervisedCapable: z.number().int().nonnegative(),
      safetyMonitorOnly: z.number().int().nonnegative(),
      totalActiveVehicles: z.number().int().nonnegative(),
    }),
  }),
  jobPostings: z.object({
    title: z.string(),
    data: z.array(MetricDataPointSchema),
  }),
  fsdApprovals: z.object({
    title: z.string(),
    countries: z.array(z.object({
      name: z.string(),
      status: z.string(),
      date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(), // Can be missing
      note: z.string().optional(),
    })),
  }),
})

// Category schemas
const TimelineEventSchema = z.object({
  date: z.string(), // Can be various formats (YYYY-MM-DD, Q1 2025, etc.)
  event: z.string(),
})

const CategorySchema = z.object({
  title: z.string(),
  latestUpdate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  criticalNews: z.string(),
  keyPoints: z.array(z.string()).optional(),
  timeline: z.array(TimelineEventSchema).optional(),
})

// Production & Delivery schemas
const QuarterlyDataSchema = z.object({
  quarter: z.string(),
  production: z.union([
    z.number().int().nonnegative(),
    z.object({ // New format with breakdown
      total: z.number().int().nonnegative(),
      model3Y: z.number().int().nonnegative().optional(),
      otherModels: z.number().int().nonnegative().optional(),
    })
  ]).nullable(), // Can be null for older quarters
  delivery: z.number().int().nonnegative().optional(), // Old field name
  deliveries: z.object({ // New format
    total: z.number().int().nonnegative(),
    model3Y: z.number().int().nonnegative().optional(),
    otherModels: z.number().int().nonnegative().optional(),
  }).optional(),
  energyStorage: z.object({
    deployed_gwh: z.number(),
    note: z.string().optional(),
  }).optional(),
})

const AnnualSummarySchema = z.object({
  year: z.string(),
  deliveries: z.number().int().nonnegative(),
  yoyGrowth: z.number().nullable(), // Can be null for first year
})

const ProductionDeliveryCategorySchema = z.object({
  title: z.string(),
  latestUpdate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  criticalNews: z.string(),
  totalProduction: z.string(),
  totalDeliveries: z.string(),
  quarterlyData: z.array(QuarterlyDataSchema),
  annualSummary: z.array(AnnualSummarySchema),
})

// Main data schema
export const TeslaDataSchema = z.object({
  lastUpdated: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Must be YYYY-MM-DD format'),
  weeklySummaries: z.array(WeeklySummarySchema),
  metrics: MetricsSchema,
  categories: z.object({
    aiChip: CategorySchema,
    battery4680: CategorySchema,
    cybercab: CategorySchema,
    fsd: CategorySchema,
    jobPostings: CategorySchema,
    optimus: CategorySchema,
    productionDelivery: ProductionDeliveryCategorySchema,
    terafab: CategorySchema,
  }),
})

// Export type inferred from schema
export type TeslaData = z.infer<typeof TeslaDataSchema>

// Validation function with detailed error reporting
export function validateTeslaData(data: unknown): { success: true; data: TeslaData } | { success: false; errors: string[] } {
  const result = TeslaDataSchema.safeParse(data)

  if (result.success) {
    return { success: true, data: result.data }
  }

  const errors = result.error.issues.map((err) => {
    const path = err.path.join('.')
    return `${path}: ${err.message}`
  })

  return { success: false, errors }
}

// Additional validation rules
export function validateDataInvariants(data: TeslaData): string[] {
  const errors: string[] = []

  // Check weekly summaries are in reverse chronological order
  const weeks = data.weeklySummaries.map(w => w.weekOf)
  for (let i = 0; i < weeks.length - 1; i++) {
    if (weeks[i] < weeks[i + 1]) {
      errors.push(`Weekly summaries not in reverse chronological order: ${weeks[i]} comes before ${weeks[i + 1]}`)
    }
  }

  // Check for duplicate weeks
  const weekSet = new Set(weeks)
  if (weekSet.size !== weeks.length) {
    errors.push(`Duplicate weekly summaries found`)
  }

  // Check all metric dates are valid
  const checkMetricDates = (metricData: Array<{ date: string }>, metricName: string) => {
    for (let i = 0; i < metricData.length - 1; i++) {
      if (metricData[i].date > metricData[i + 1].date) {
        // Metrics should be in chronological order
        errors.push(`${metricName} data not in chronological order: ${metricData[i].date} after ${metricData[i + 1].date}`)
      }
    }
  }

  checkMetricDates(data.metrics.cybercab.data, 'Cybercab')
  checkMetricDates(data.metrics.robotaxiFleet.data, 'RobotaxiFleet')
  checkMetricDates(data.metrics.jobPostings.data, 'JobPostings')

  // Check robotaxi breakdown consistency
  const cities = data.metrics.robotaxiCities
  const totalActiveVehicles = cities.cities.reduce((sum, city) => sum + (city.activeVehicles ?? 0), 0)
  if (totalActiveVehicles !== cities.summary.totalActiveVehicles) {
    errors.push(`RobotaxiCities summary mismatch: sum of city vehicles (${totalActiveVehicles}) != summary total (${cities.summary.totalActiveVehicles})`)
  }

  // Check category keys match keyChanges
  const validCategories = new Set([
    'AI Chip Production',
    'Cybercab Production',
    'FSD Country Approvals',
    'Job Postings',
    'Optimus Production',
    'Vehicle Production & Delivery',
    'Terafab In-House Chip Manufacturing',
    '4680 Battery Cell Production',
    'FSD v15 Software'
  ])

  data.weeklySummaries.forEach((week, idx) => {
    week.keyChanges.forEach((change, cidx) => {
      if (!validCategories.has(change.category)) {
        errors.push(`weeklySummaries[${idx}].keyChanges[${cidx}].category "${change.category}" is not a recognized category`)
      }
    })
  })

  return errors
}
