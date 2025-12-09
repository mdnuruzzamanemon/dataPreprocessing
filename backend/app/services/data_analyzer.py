import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Dict, Any
import os
from app.models.schemas import (
    AnalysisResponse, DataIssue, IssueType, IssueSeverity, FileInfo
)
from app.services.file_handler import FileHandler
from app.core.config import settings
import re

class DataAnalyzer:
    """Analyze datasets for data quality issues"""
    
    def __init__(self):
        self.file_handler = FileHandler()
    
    async def analyze_dataset(self, file_id: str, exclude_skewness_columns: set = None) -> AnalysisResponse:
        """Perform comprehensive analysis on the dataset"""
        df = self.file_handler.load_dataframe(file_id)
        issues: List[DataIssue] = []
        
        # Run all checks
        issues.extend(self._check_missing_values(df))
        issues.extend(self._check_duplicates(df))
        issues.extend(self._check_outliers(df))
        issues.extend(self._check_data_types(df))
        issues.extend(self._check_categorical_issues(df))
        issues.extend(self._check_constant_features(df))
        issues.extend(self._check_correlated_features(df))
        issues.extend(self._check_skewness(df, exclude_columns=exclude_skewness_columns))
        issues.extend(self._check_high_cardinality(df))
        issues.extend(self._check_date_formats(df))
        issues.extend(self._check_text_issues(df))
        issues.extend(self._check_imbalanced_data(df))
        
        # Create summary
        summary = self._create_summary(issues)
        
        # Get file info
        file_path = self.file_handler._get_file_path(file_id)
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_path)[1][1:]
        
        file_info = FileInfo(
            file_id=file_id,
            filename=f"{file_id}.{file_ext}",
            rows=len(df),
            columns=len(df.columns),
            size=file_size,
            file_type=file_ext
        )
        
        return AnalysisResponse(
            file_id=file_id,
            file_info=file_info,
            issues=issues,
            total_issues=len(issues),
            summary=summary
        )
    
    def _check_missing_values(self, df: pd.DataFrame) -> List[DataIssue]:
        """Check for missing values"""
        issues = []
        missing = df.isnull().sum()
        missing_cols = missing[missing > 0]
        
        # Debug: Print to console
        print(f"DEBUG: Total missing values: {missing.sum()}")
        print(f"DEBUG: Missing per column: {missing_cols.to_dict()}")
        print(f"DEBUG: DataFrame shape: {df.shape}")
        print(f"DEBUG: DataFrame dtypes: {df.dtypes.to_dict()}")
        
        if len(missing_cols) > 0:
            total_cells = len(df) * len(df.columns)
            total_missing = missing.sum()
            
            issues.append(DataIssue(
                type=IssueType.MISSING_VALUES,
                severity=self._get_severity(total_missing / total_cells),
                affected_columns=missing_cols.index.tolist(),
                description=f"Found {total_missing} missing values across {len(missing_cols)} columns",
                count=int(total_missing),
                percentage=round((total_missing / total_cells) * 100, 2),
                details={col: int(count) for col, count in missing_cols.items()},
                recommended_actions=["Fill with mean", "Fill with median", "Fill with mode", "Drop rows"]
            ))
        
        return issues
    
    def _check_duplicates(self, df: pd.DataFrame) -> List[DataIssue]:
        """Check for duplicate rows"""
        issues = []
        duplicates = df.duplicated().sum()
        
        if duplicates > 0:
            issues.append(DataIssue(
                type=IssueType.DUPLICATES,
                severity=self._get_severity(duplicates / len(df)),
                affected_columns=df.columns.tolist(),
                description=f"Found {duplicates} duplicate rows",
                count=int(duplicates),
                percentage=round((duplicates / len(df)) * 100, 2),
                details={"duplicate_rows": int(duplicates)},
                recommended_actions=["Remove duplicates"]
            ))
        
        return issues
    
    def _check_outliers(self, df: pd.DataFrame) -> List[DataIssue]:
        """Check for outliers in numerical columns"""
        issues = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_cols = {}
        
        for col in numeric_cols:
            # Skip if column has too few non-null values
            if df[col].notna().sum() < 4:
                continue
                
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            # Skip if IQR is 0 (all values are same)
            if IQR == 0:
                continue
                
            lower_bound = Q1 - settings.OUTLIER_THRESHOLD * IQR
            upper_bound = Q3 + settings.OUTLIER_THRESHOLD * IQR
            
            outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            if outliers > 0:
                outlier_cols[col] = int(outliers)
        
        if outlier_cols:
            total_outliers = sum(outlier_cols.values())
            issues.append(DataIssue(
                type=IssueType.OUTLIERS,
                severity=IssueSeverity.MEDIUM,
                affected_columns=list(outlier_cols.keys()),
                description=f"Found outliers in {len(outlier_cols)} numerical columns",
                count=total_outliers,
                details=outlier_cols,
                recommended_actions=["Remove outliers", "Cap values (IQR)", "Log transform"]
            ))
        
        return issues
    
    def _check_data_types(self, df: pd.DataFrame) -> List[DataIssue]:
        """Check for inconsistent data types"""
        issues = []
        inconsistent_cols = []
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if column contains mixed types
                try:
                    numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
                    if 0 < numeric_count < len(df[col].dropna()):
                        inconsistent_cols.append(col)
                except:
                    pass
        
        if inconsistent_cols:
            issues.append(DataIssue(
                type=IssueType.INCONSISTENT_TYPES,
                severity=IssueSeverity.HIGH,
                affected_columns=inconsistent_cols,
                description=f"Found {len(inconsistent_cols)} columns with mixed data types",
                count=len(inconsistent_cols),
                details={col: str(df[col].dtype) for col in inconsistent_cols},
                recommended_actions=["Convert to appropriate type", "Clean inconsistent values"]
            ))
        
        return issues
    
    def _check_categorical_issues(self, df: pd.DataFrame) -> List[DataIssue]:
        """Check for categorical data issues"""
        issues = []
        categorical_cols = df.select_dtypes(include=['object']).columns
        problematic_cols = {}
        
        for col in categorical_cols:
            unique_values = df[col].dropna().unique()
            # Check for inconsistent naming (e.g., 'yes', 'Yes', 'YES')
            if len(unique_values) > 1:
                lower_values = [str(v).lower().strip() for v in unique_values]
                if len(set(lower_values)) < len(unique_values):
                    problematic_cols[col] = list(unique_values[:5])  # Sample
        
        if problematic_cols:
            issues.append(DataIssue(
                type=IssueType.CATEGORICAL_INCONSISTENCIES,
                severity=IssueSeverity.MEDIUM,
                affected_columns=list(problematic_cols.keys()),
                description=f"Found categorical inconsistencies in {len(problematic_cols)} columns",
                count=len(problematic_cols),
                details=problematic_cols,
                recommended_actions=["Normalize naming", "Apply label encoding", "Apply one-hot encoding"]
            ))
        
        return issues
    
    def _check_constant_features(self, df: pd.DataFrame) -> List[DataIssue]:
        """Check for constant or near-constant features"""
        issues = []
        constant_cols = []
        
        for col in df.columns:
            if df[col].nunique() == 1:
                constant_cols.append(col)
        
        if constant_cols:
            issues.append(DataIssue(
                type=IssueType.CONSTANT_VALUES,
                severity=IssueSeverity.LOW,
                affected_columns=constant_cols,
                description=f"Found {len(constant_cols)} constant-value columns",
                count=len(constant_cols),
                details={col: str(df[col].iloc[0]) for col in constant_cols},
                recommended_actions=["Remove constant columns"]
            ))
        
        return issues
    
    def _check_correlated_features(self, df: pd.DataFrame) -> List[DataIssue]:
        """Check for highly correlated features"""
        issues = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr().abs()
            upper_triangle = corr_matrix.where(
                np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
            )
            
            high_corr = []
            for col in upper_triangle.columns:
                corr_cols = upper_triangle[col][upper_triangle[col] > settings.CORRELATION_THRESHOLD]
                if len(corr_cols) > 0:
                    for corr_col in corr_cols.index:
                        high_corr.append((col, corr_col, round(corr_cols[corr_col], 2)))
            
            if high_corr:
                issues.append(DataIssue(
                    type=IssueType.CORRELATED_FEATURES,
                    severity=IssueSeverity.LOW,
                    affected_columns=list(set([c[0] for c in high_corr] + [c[1] for c in high_corr])),
                    description=f"Found {len(high_corr)} pairs of highly correlated features",
                    count=len(high_corr),
                    details={"correlations": [{"col1": c[0], "col2": c[1], "correlation": c[2]} for c in high_corr]},
                    recommended_actions=["Remove one of correlated features", "Apply PCA"]
                ))
        
        return issues
    
    def _check_skewness(self, df: pd.DataFrame, exclude_columns: set = None) -> List[DataIssue]:
        """Check for skewed distributions"""
        issues = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        skewed_cols = {}
        
        for col in numeric_cols:
            # Skip excluded columns (previously failed transformations)
            if exclude_columns and col in exclude_columns:
                continue
                
            # Skip columns with too few unique values (can't be meaningfully transformed)
            unique_count = df[col].nunique()
            if unique_count < 5:
                continue
                
            # Skip columns with insufficient variation
            col_min, col_max = df[col].min(), df[col].max()
            if col_max - col_min < 0.01:
                continue
            
            skewness = df[col].skew()
            # Add tolerance to prevent re-detection of marginally skewed columns after transformation
            # If threshold is 1.0, only flag if skewness > 1.1 (10% tolerance)
            detection_threshold = settings.SKEWNESS_THRESHOLD * 1.1
            if abs(skewness) > detection_threshold:
                skewed_cols[col] = round(skewness, 2)
        
        if skewed_cols:
            issues.append(DataIssue(
                type=IssueType.SKEWNESS,
                severity=IssueSeverity.MEDIUM,
                affected_columns=list(skewed_cols.keys()),
                description=f"Found {len(skewed_cols)} columns with skewed distributions",
                count=len(skewed_cols),
                details=skewed_cols,
                recommended_actions=["Apply log transform", "Apply square root transform", "Apply Box-Cox transform"]
            ))
        
        return issues
    
    def _check_high_cardinality(self, df: pd.DataFrame) -> List[DataIssue]:
        """Check for high cardinality categorical features"""
        issues = []
        categorical_cols = df.select_dtypes(include=['object']).columns
        high_card_cols = {}
        
        for col in categorical_cols:
            unique_count = df[col].nunique()
            if unique_count > settings.HIGH_CARDINALITY_THRESHOLD:
                high_card_cols[col] = unique_count
        
        if high_card_cols:
            issues.append(DataIssue(
                type=IssueType.HIGH_CARDINALITY,
                severity=IssueSeverity.MEDIUM,
                affected_columns=list(high_card_cols.keys()),
                description=f"Found {len(high_card_cols)} columns with high cardinality",
                count=len(high_card_cols),
                details=high_card_cols,
                recommended_actions=["Group rare categories", "Use target encoding", "Remove column"]
            ))
        
        return issues
    
    def _check_date_formats(self, df: pd.DataFrame) -> List[DataIssue]:
        """Check for wrong or inconsistent date formats"""
        issues = []
        date_cols = []
        
        for col in df.select_dtypes(include=['object']).columns:
            sample = df[col].dropna().head(100)
            # Check if column might contain dates
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
            ]
            
            matches = sum(sample.astype(str).str.contains('|'.join(date_patterns), regex=True))
            if matches > len(sample) * 0.5:  # If more than 50% match date patterns
                try:
                    pd.to_datetime(sample, errors='coerce')
                    date_cols.append(col)
                except:
                    pass
        
        if date_cols:
            issues.append(DataIssue(
                type=IssueType.WRONG_DATE_FORMAT,
                severity=IssueSeverity.MEDIUM,
                affected_columns=date_cols,
                description=f"Found {len(date_cols)} columns that may need date formatting",
                count=len(date_cols),
                details={col: "Inconsistent date format detected" for col in date_cols},
                recommended_actions=["Convert to standard format", "Extract date components"]
            ))
        
        return issues
    
    def _check_text_issues(self, df: pd.DataFrame) -> List[DataIssue]:
        """Check for noisy text data"""
        issues = []
        text_cols = df.select_dtypes(include=['object']).columns
        noisy_cols = []
        
        for col in text_cols:
            sample = df[col].dropna().head(100).astype(str)
            # Check for excessive punctuation or special characters
            special_char_ratio = sample.str.count(r'[^a-zA-Z0-9\s]').mean() / sample.str.len().mean()
            if special_char_ratio > 0.2:  # If more than 20% special chars
                noisy_cols.append(col)
        
        if noisy_cols:
            issues.append(DataIssue(
                type=IssueType.NOISY_TEXT,
                severity=IssueSeverity.LOW,
                affected_columns=noisy_cols,
                description=f"Found {len(noisy_cols)} text columns with potential noise",
                count=len(noisy_cols),
                details={col: "High ratio of special characters detected" for col in noisy_cols},
                recommended_actions=["Convert to lowercase", "Remove punctuation", "Remove stopwords"]
            ))
        
        return issues
    
    def _check_imbalanced_data(self, df: pd.DataFrame) -> List[DataIssue]:
        """Check for imbalanced target columns"""
        issues = []
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            if len(value_counts) > 1 and len(value_counts) < 10:  # Likely a target variable
                ratio = value_counts.max() / value_counts.min()
                if ratio > 3:  # Imbalance threshold
                    issues.append(DataIssue(
                        type=IssueType.IMBALANCED_DATA,
                        severity=IssueSeverity.MEDIUM,
                        affected_columns=[col],
                        description=f"Column '{col}' has imbalanced class distribution",
                        count=1,
                        details={
                            "distribution": value_counts.to_dict(),
                            "imbalance_ratio": round(ratio, 2)
                        },
                        recommended_actions=["Apply SMOTE", "Undersample majority class", "Oversample minority class"]
                    ))
        
        return issues
    
    def _get_severity(self, percentage: float) -> IssueSeverity:
        """Determine severity based on percentage"""
        if percentage < 0.05:
            return IssueSeverity.LOW
        elif percentage < 0.15:
            return IssueSeverity.MEDIUM
        elif percentage < 0.30:
            return IssueSeverity.HIGH
        else:
            return IssueSeverity.CRITICAL
    
    def _create_summary(self, issues: List[DataIssue]) -> Dict[str, int]:
        """Create summary of issues by severity"""
        summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for issue in issues:
            summary[issue.severity.value] += 1
        
        return summary
    
    async def get_data_preview(self, file_id: str, rows: int = 10) -> Dict[str, Any]:
        """Get a preview of the dataset"""
        df = self.file_handler.load_dataframe(file_id)
        
        return {
            "columns": df.columns.tolist(),
            "data": df.head(rows).to_dict(orient='records'),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "shape": df.shape
        }
