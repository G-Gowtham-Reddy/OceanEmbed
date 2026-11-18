export type PageId =
  | 'dashboard'
  | '3d-ocean'
  | 'prediction'
  | 'model-eval'
  | 'about'
  | 'explorer'
  | '3d-temp'
  | 'model-analysis'
  | 'argo-validation'
  | 'preprocessing';

export interface RegionInfo {
  id: string;
  name: string;
  coordinates: string;
  lat: number;
  lon: number;
  baseSst: number;
  baseMld: number;
  thermoclineDepth: number;
  activeFloats: number;
  profileCount?: number;
  description?: string;
}

export interface OceanApiResponse {
  region: string;
  regionId: string;
  coordinates: string;
  lat: number;
  lon: number;
  date: string;
  maxDepth: number;
  kpis: {
    surfaceTemp: number;
    mld: number;
    thermoclineDepth: number;
    targetDepthTemp: number;
    activeFloats: number;
  };
  layers: {
    name: string;
    depthRange: string;
    tempRange: string;
    description: string;
  }[];
  profile: {
    depth: number;
    temperature: number;
    label: string;
  }[];
}

export interface FilterState {
  region: string;
  date: string;
  parameter?: string;
  variable?: string;
  depthRange: [number, number];
}

export interface OceanStation {
  id: string;
  wmoId: string;
  lat: number;
  lon: number;
  date: string;
  surfaceTemp: number;
  bottomTemp: number;
  mld: number;
  profilesCount: number;
  qualityFlag: 'Good' | 'Adjusted' | 'Suspect';
}

export interface ModelMetricItem {
  depth: number;
  architecture: string;
  r2_score: number;
  rmse: number;
  mae: number;
  bias: number;
  baseline_r2: number;
  baseline_rmse: number;
  rmse_improvement: number;
}

export interface ModelMetricsApiResponse {
  status: string;
  total_depths: number;
  validation_strategy: string;
  metrics_by_depth: ModelMetricItem[];
  validation_report: Record<string, any>;
  feature_attributions: Record<string, any>;
}

export interface PredictionRequestData {
  sat_sst: number;
  sat_sla: number;
  sat_current_u: number;
  sat_current_v: number;
  latitude: number;
  longitude: number;
  date?: string;
}

export interface PredictionResponseData {
  status: string;
  date: string;
  latitude: number;
  longitude: number;
  basin: string;
  kpis: {
    surfaceTemp: number;
    mld: number;
    thermoclineDepth: number;
    targetDepthTemp: number;
    minTemp: number;
    maxTemp: number;
  };
  profile: {
    depth: number;
    temperature: number;
    expected_rmse?: number;
    expected_r2?: number;
    label: string;
  }[];
  layers: {
    name: string;
    depthRange: string;
    tempRange: string;
    description: string;
  }[];
  feature_attributions: Record<string, string>;
}

export interface ArgoProfileItem {
  profile_id: string;
  float_wmo: number;
  cycle_number: number;
  date: string;
  latitude: number;
  longitude: number;
  basin: string;
  sat_sst: number;
  sat_sla: number;
  sat_current_u?: number;
  sat_current_v?: number;
  surface_temp?: number;
  thermocline_temp_100m?: number;
  deep_temp_500m?: number;
}
