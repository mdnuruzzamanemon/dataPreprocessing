export interface FileInfo {
  file_id: string;
  filename: string;
  rows: number;
  columns: number;
  size: number;
  file_type: string;
}

export enum IssueSeverity {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical"
}

export enum IssueType {
  MISSING_VALUES = "missing_values",
  DUPLICATES = "duplicates",
  OUTLIERS = "outliers",
  IMBALANCED_DATA = "imbalanced_data",
  INCONSISTENT_TYPES = "inconsistent_types",
  CATEGORICAL_INCONSISTENCIES = "categorical_inconsistencies",
  INVALID_RANGES = "invalid_ranges",
  SKEWNESS = "skewness",
  HIGH_CARDINALITY = "high_cardinality",
  CONSTANT_VALUES = "constant_values",
  CORRELATED_FEATURES = "correlated_features",
  WRONG_DATE_FORMAT = "wrong_date_format",
  ENCODING_ISSUES = "encoding_issues",
  MIXED_UNITS = "mixed_units",
  NOISY_TEXT = "noisy_text"
}

export interface DataIssue {
  type: IssueType;
  severity: IssueSeverity;
  affected_columns: string[];
  description: string;
  count?: number;
  percentage?: number;
  details: Record<string, any>;
  recommended_actions: string[];
}

export interface AnalysisResponse {
  file_id: string;
  file_info: FileInfo;
  issues: DataIssue[];
  total_issues: number;
  summary: Record<string, number>;
}

export interface PreprocessAction {
  issue_type: IssueType;
  columns: string[];
  method: string;
  parameters?: Record<string, any>;
}

export interface PreprocessRequest {
  actions: PreprocessAction[];
}

export interface PreprocessResponse {
  file_id: string;
  original_rows: number;
  processed_rows: number;
  applied_actions: Array<{
    issue_type: string;
    columns: string[];
    method: string;
    status: string;
    error?: string;
  }>;
  download_url: string;
  summary: Record<string, any>;
}

export interface DataPreview {
  columns: string[];
  data: Record<string, any>[];
  dtypes: Record<string, string>;
  shape: [number, number];
}
