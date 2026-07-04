// Tesla tracking data types

export interface WeeklySummary {
  weekOf: string;
  keyChanges: KeyChange[];
  trends: string[];
}

export interface KeyChange {
  status: 'positive' | 'negative' | 'neutral';
  sentiment?: {
    headline: string;
    reality: string;
    confidence: 'high' | 'medium' | 'low';
    rationale: string;
  };
  evidence?: {
    positive_signals: string[];
    negative_signals: string[];
    key_metrics: {
      actual: string;
      target: string;
      trajectory: string;
    };
  };
  category: string;
  title: string;
  description: string;
  source: string;
}

export interface QuarterlyData {
  quarter: string;
  production: number;
  delivery: number;
}

export interface AnnualSummary {
  year: string;
  deliveries: number;
  yoyGrowth: number;
}

export interface ProductionDeliveryCategory {
  title: string;
  latestUpdate: string;
  criticalNews: string;
  totalProduction: string;
  totalDeliveries: string;
  quarterlyData: QuarterlyData[];
  annualSummary: AnnualSummary[];
}

export interface MetricDataPoint {
  date: string;
  count: number;
  note: string;
}

export interface RobotaxiCity {
  name: string;
  status: 'active' | 'mapped';
  serviceType: 'unsupervised' | 'mixed' | 'safety-monitor-only';
  vehicleType: string;
  activeVehicles: number;
  breakdown?: {
    unsupervised: number;
    safetyMonitor: number;
    cybercabTesting?: number;
  };
  launchDate: string | null;
  serviceArea: string;
  notes: string;
}

export interface Metrics {
  cybercab: {
    title: string;
    data: MetricDataPoint[];
  };
  robotaxiFleet: {
    title: string;
    data: MetricDataPoint[];
    target: string;
    breakdown: {
      active: number;
      staged: number;
      cities: string[];
    };
  };
  robotaxiCities: {
    title: string;
    lastUpdated: string;
    cities: RobotaxiCity[];
    summary: {
      totalCities: number;
      activeCities: number;
      mappedOnly: number;
      unsupervisedCapable: number;
      safetyMonitorOnly: number;
      totalActiveVehicles: number;
    };
  };
  jobPostings: {
    title: string;
    data: MetricDataPoint[];
  };
  fsdApprovals: {
    title: string;
    countries: Array<{
      name: string;
      status: string;
      date: string;
      note?: string;
    }>;
  };
}

export interface Category {
  title: string;
  latestUpdate: string;
  criticalNews: string;
  keyPoints?: string[];
  timeline?: Array<{
    date: string;
    event: string;
  }>;
}

export interface TeslaData {
  lastUpdated: string;
  weeklySummaries: WeeklySummary[];
  metrics: Metrics;
  categories: {
    aiChip: Category;
    cybercab: Category;
    fsd: Category;
    jobPostings: Category;
    optimus: Category;
    productionDelivery: ProductionDeliveryCategory;
  };
}
