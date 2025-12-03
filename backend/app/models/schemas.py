from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum

class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IssueType(str, Enum):
    MISSING_VALUES = "missing_values"
    DUPLICATES = "duplicates"
    OUTLIERS = "outliers"
    IMBALANCED_DATA = "imbalanced_data"
    INCONSISTENT_TYPES = "inconsistent_types"
    CATEGORICAL_INCONSISTENCIES = "categorical_inconsistencies"
    INVALID_RANGES = "invalid_ranges"
    SKEWNESS = "skewness"
    HIGH_CARDINALITY = "high_cardinality"
    CONSTANT_VALUES = "constant_values"
    CORRELATED_FEATURES = "correlated_features"
    WRONG_DATE_FORMAT = "wrong_date_format"
    ENCODING_ISSUES = "encoding_issues"
    MIXED_UNITS = "mixed_units"
    NOISY_TEXT = "noisy_text"

class FileInfo(BaseModel):
    file_id: str
    filename: str
    rows: int
    columns: int
    size: int
    file_type: str

class DataIssue(BaseModel):
    type: IssueType
    severity: IssueSeverity
    affected_columns: List[str]
    description: str
    count: Optional[int] = None
    percentage: Optional[float] = None
    details: Dict[str, Any] = {}
    recommended_actions: List[str] = []

class AnalysisResponse(BaseModel):
    file_id: str
    file_info: FileInfo
    issues: List[DataIssue]
    total_issues: int
    summary: Dict[str, int]

class PreprocessAction(BaseModel):
    issue_type: IssueType
    columns: List[str]
    method: str
    parameters: Optional[Dict[str, Any]] = {}

class PreprocessRequest(BaseModel):
    actions: List[PreprocessAction]

class PreprocessResponse(BaseModel):
    file_id: str
    original_rows: int
    processed_rows: int
    applied_actions: List[Dict[str, Any]]
    download_url: str
    summary: Dict[str, Any]
