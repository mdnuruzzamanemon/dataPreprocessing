import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler, RobustScaler
from typing import List, Dict, Any
from app.models.schemas import PreprocessAction, PreprocessResponse, IssueType, DataIssue, IssueSeverity
from app.services.file_handler import FileHandler
from app.services.data_analyzer import DataAnalyzer
import re

class DataPreprocessor:
    """Apply preprocessing transformations to datasets"""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.analyzer = DataAnalyzer()
    
    async def preprocess_dataset(
        self, 
        file_id: str, 
        actions: List[PreprocessAction]
    ) -> PreprocessResponse:
        """Apply preprocessing actions to dataset"""
        print(f"\n=== PREPROCESSING START ===")
        print(f"File ID: {file_id}")
        print(f"Number of actions: {len(actions)}")
        
        df = self.file_handler.load_dataframe(file_id)
        df = df.copy()  # Create a copy to avoid mutation issues
        original_rows = len(df)
        print(f"Original rows: {original_rows}")
        print(f"Missing values before: {df.isna().sum().sum()}")
        applied_actions = []
        
        # Apply each action
        for action in actions:
            try:
                print(f"\nApplying action:")
                print(f"  Issue Type: {action.issue_type}")
                print(f"  Columns: {action.columns}")
                print(f"  Method: {action.method}")
                
                df = self._apply_action(df, action)
                
                print(f"  ✓ Success - Rows after: {len(df)}")
                applied_actions.append({
                    "issue_type": action.issue_type.value,
                    "columns": action.columns,
                    "method": action.method,
                    "status": "success"
                })
            except Exception as e:
                print(f"  ✗ Failed: {str(e)}")
                applied_actions.append({
                    "issue_type": action.issue_type.value,
                    "columns": action.columns,
                    "method": action.method,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Save processed data
        print(f"\n=== FINAL VERIFICATION BEFORE SAVE ===")
        print(f"DataFrame shape: {df.shape}")
        print(f"Missing values after all actions: {df.isna().sum().sum()}")
        print(f"Missing values per column:")
        for col in df.columns:
            na_count = df[col].isna().sum()
            if na_count > 0:
                print(f"  {col}: {na_count}")
        
        processed_path = self.file_handler.save_processed_dataframe(file_id, df)
        print(f"=== PREPROCESSING COMPLETE ===\n")
        
        return PreprocessResponse(
            file_id=file_id,
            original_rows=original_rows,
            processed_rows=len(df),
            applied_actions=applied_actions,
            download_url=f"/api/download/{file_id}",
            summary={
                "rows_removed": original_rows - len(df),
                "columns": len(df.columns),
                "actions_applied": len([a for a in applied_actions if a["status"] == "success"])
            }
        )
    
    def _apply_action(self, df: pd.DataFrame, action: PreprocessAction) -> pd.DataFrame:
        """Apply a single preprocessing action"""
        issue_type = action.issue_type
        columns = action.columns
        method = action.method
        
        if issue_type == IssueType.MISSING_VALUES:
            return self._handle_missing_values(df, columns, method)
        elif issue_type == IssueType.DUPLICATES:
            return self._handle_duplicates(df, method)
        elif issue_type == IssueType.OUTLIERS:
            return self._handle_outliers(df, columns, method)
        elif issue_type == IssueType.CATEGORICAL_INCONSISTENCIES:
            return self._handle_categorical(df, columns, method)
        elif issue_type == IssueType.WRONG_DATE_FORMAT:
            return self._handle_dates(df, columns, method, action.parameters)
        elif issue_type == IssueType.NOISY_TEXT:
            return self._handle_text(df, columns, method)
        elif issue_type == IssueType.CONSTANT_VALUES:
            return self._remove_columns(df, columns)
        elif issue_type == IssueType.SKEWNESS:
            return self._handle_skewness(df, columns, method)
        elif issue_type == IssueType.HIGH_CARDINALITY:
            return self._handle_high_cardinality(df, columns, method)
        elif issue_type == IssueType.CORRELATED_FEATURES:
            return self._handle_correlated_features(df, columns)
        elif issue_type == IssueType.INCONSISTENT_TYPES:
            return self._handle_inconsistent_types(df, columns)
        else:
            print(f"    WARNING: No handler for issue type {issue_type}")
            return df
    
    def _handle_missing_values(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        method: str
    ) -> pd.DataFrame:
        """Handle missing values"""
        df = df.copy()  # Ensure we're working with a copy
        
        for col in columns:
            if col not in df.columns:
                print(f"    WARNING: Column '{col}' not found in DataFrame")
                continue
            
            missing_before = df[col].isna().sum()
            print(f"    Column '{col}': {missing_before} missing values")
            
            if missing_before == 0:
                print(f"    No missing values to fix")
                continue
            
            if method == "mean":
                if pd.api.types.is_numeric_dtype(df[col]):
                    mean_val = df[col].mean()
                    df[col] = df[col].fillna(mean_val)
                    print(f"    Filled with mean: {mean_val}")
                else:
                    print(f"    WARNING: Cannot use mean on non-numeric column, skipping")
                    
            elif method == "median":
                if pd.api.types.is_numeric_dtype(df[col]):
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                    print(f"    Filled with median: {median_val}")
                else:
                    print(f"    WARNING: Cannot use median on non-numeric column, skipping")
                    
            elif method == "mode":
                mode_val = df[col].mode()
                if not mode_val.empty:
                    df[col] = df[col].fillna(mode_val[0])
                    print(f"    Filled with mode: {mode_val[0]}")
                else:
                    print(f"    WARNING: No mode found, skipping")
                    
            elif method == "forward_fill":
                df[col] = df[col].ffill()
                print(f"    Applied forward fill")
                
            elif method == "backward_fill":
                df[col] = df[col].bfill()
                print(f"    Applied backward fill")
                
            elif method == "drop":
                rows_before = len(df)
                df = df.dropna(subset=[col])
                rows_dropped = rows_before - len(df)
                print(f"    Dropped {rows_dropped} rows")
            
            missing_after = df[col].isna().sum()
            print(f"    After {method}: {missing_after} missing values (fixed {missing_before - missing_after})")
            
            # Verify the fix worked
            if missing_after > 0 and method != "forward_fill" and method != "backward_fill":
                print(f"    WARNING: Still has {missing_after} missing values after {method}!")
        
        return df
    
    def _handle_duplicates(self, df: pd.DataFrame, method: str) -> pd.DataFrame:
        """Handle duplicate rows"""
        if method == "remove":
            duplicates_before = df.duplicated().sum()
            print(f"    Duplicates before: {duplicates_before}")
            df = df.drop_duplicates()
            duplicates_after = df.duplicated().sum()
            print(f"    Duplicates after: {duplicates_after} (removed {duplicates_before - duplicates_after})")
        return df
    
    def _handle_outliers(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        method: str
    ) -> pd.DataFrame:
        """Handle outliers"""
        for col in columns:
            if col not in df.columns:
                continue
            
            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(df[col]):
                print(f"    Skipping non-numeric column '{col}'")
                continue
            
            outliers_before = 0
            if method == "remove":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers_before = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                print(f"    Column '{col}': Removed {outliers_before} outliers")
            
            elif method == "cap":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers_before = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                print(f"    Column '{col}': Capped {outliers_before} outliers")
            
            elif method == "log_transform":
                # Add small constant to avoid log(0)
                min_val = df[col].min()
                if min_val <= 0:
                    df[col] = np.log1p(df[col] - min_val + 1)
                else:
                    df[col] = np.log1p(df[col])
                print(f"    Column '{col}': Applied log transform")
        
        return df
    
    def _handle_categorical(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        method: str
    ) -> pd.DataFrame:
        """Handle categorical data"""
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == "normalize":
                # Save the NaN mask before normalization
                na_mask = df[col].isna()
                unique_before = df[col].nunique()
                
                # Normalize only non-NaN values
                df[col] = df[col].astype(str).str.lower().str.strip()
                
                # Restore NaN values (don't convert NaN to "nan" string)
                df.loc[na_mask, col] = np.nan
                
                unique_after = df[col].nunique()
                print(f"    Column '{col}': Normalized - {unique_before} → {unique_after} unique values")
            
            elif method == "label_encode":
                le = LabelEncoder()
                # Handle NaN by filling temporarily, then restoring
                na_mask = df[col].isna()
                df[col] = df[col].fillna('__MISSING__')
                df[col] = le.fit_transform(df[col].astype(str))
                df.loc[na_mask, col] = np.nan
                print(f"    Column '{col}': Label encoded to {df[col].nunique()} numeric values")
            
            elif method == "one_hot":
                unique_vals = df[col].nunique()
                dummies = pd.get_dummies(df[col], prefix=col, dummy_na=True)
                df = pd.concat([df.drop(col, axis=1), dummies], axis=1)
                print(f"    Column '{col}': One-hot encoded to {unique_vals} new columns")
        
        return df
        
        return df
    
    def _handle_dates(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        method: str,
        parameters: Dict[str, Any]
    ) -> pd.DataFrame:
        """Handle date columns"""
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == "convert":
                df[col] = pd.to_datetime(df[col], errors='coerce')
                target_format = parameters.get('format', '%Y-%m-%d')
                df[col] = df[col].dt.strftime(target_format)
            
            elif method == "extract":
                df[col] = pd.to_datetime(df[col], errors='coerce')
                extract_parts = parameters.get('parts', ['year', 'month', 'day'])
                
                if 'year' in extract_parts:
                    df[f'{col}_year'] = df[col].dt.year
                if 'month' in extract_parts:
                    df[f'{col}_month'] = df[col].dt.month
                if 'day' in extract_parts:
                    df[f'{col}_day'] = df[col].dt.day
        
        return df
    
    def _handle_text(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        method: str
    ) -> pd.DataFrame:
        """Handle text data"""
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == "lowercase":
                df[col] = df[col].astype(str).str.lower()
                print(f"    Column '{col}': Converted to lowercase")
            
            elif method == "remove_punctuation":
                df[col] = df[col].astype(str).str.replace(r'[^\w\s]', '', regex=True)
                print(f"    Column '{col}': Removed punctuation")
            
            elif method == "remove_stopwords":
                # Simple stopword removal (can be enhanced with NLTK)
                stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
                df[col] = df[col].apply(
                    lambda x: ' '.join([word for word in str(x).split() if word.lower() not in stopwords])
                )
                print(f"    Column '{col}': Removed stopwords")
        
        return df
    
    def _handle_skewness(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        method: str
    ) -> pd.DataFrame:
        """Handle skewed distributions"""
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == "log_transform":
                df[col] = np.log1p(df[col] - df[col].min() + 1)
            
            elif method == "sqrt_transform":
                df[col] = np.sqrt(df[col] - df[col].min() + 1)
            
            elif method == "box_cox":
                from scipy import stats
                df[col] = stats.boxcox(df[col] - df[col].min() + 1)[0]
        
        return df
    
    def _remove_columns(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Remove specified columns"""
        return df.drop(columns=[col for col in columns if col in df.columns])
    
    def apply_scaling(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        method: str
    ) -> pd.DataFrame:
        """Apply scaling to numerical columns"""
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == "minmax":
                scaler = MinMaxScaler()
                df[col] = scaler.fit_transform(df[[col]])
            
            elif method == "standard":
                scaler = StandardScaler()
                df[col] = scaler.fit_transform(df[[col]])
            
            elif method == "robust":
                scaler = RobustScaler()
                df[col] = scaler.fit_transform(df[[col]])
        
        return df
    
    async def fix_all_issues(self, file_id: str) -> PreprocessResponse:
        """Automatically fix all detected issues with iterative refinement"""
        print(f"\\n=== ANALYZING DATA FOR AUTO-FIX ===")
        
        # Load initial data
        df = self.file_handler.load_dataframe(file_id)
        original_rows = len(df)
        all_applied_actions = []
        iteration = 0
        max_iterations = 5  # Prevent infinite loops
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\\n{'='*50}")
            print(f"ITERATION {iteration}: Checking for issues...")
            print(f"{'='*50}")
            
            # Analyze current DataFrame state directly
            issues = self._analyze_dataframe(df)
            print(f"Total issues detected: {len(issues)}")
            
            if len(issues) == 0:
                print(f"\\n✅ SUCCESS! No more issues found after {iteration} iteration(s)")
                break
            
            # Generate actions for remaining issues
            actions = []
            for issue in issues:
                print(f"  - {issue.type.value}: {len(issue.affected_columns)} columns, severity: {issue.severity.value}")
                action = self._get_recommended_action(issue)
                if action:
                    actions.append(action)
            
            if len(actions) == 0:
                print(f"\\n⚠️  No more auto-fixable issues (remaining issues require manual intervention)")
                break
            
            print(f"\\n🔧 Applying {len(actions)} fixes in iteration {iteration}...")
            
            # Order actions optimally
            action_order = {
                IssueType.DUPLICATES: 1,
                IssueType.CONSTANT_VALUES: 2,
                IssueType.CORRELATED_FEATURES: 3,
                IssueType.HIGH_CARDINALITY: 4,
                IssueType.CATEGORICAL_INCONSISTENCIES: 5,
                IssueType.INCONSISTENT_TYPES: 6,
                IssueType.OUTLIERS: 7,
                IssueType.SKEWNESS: 8,
                IssueType.NOISY_TEXT: 9,
                IssueType.WRONG_DATE_FORMAT: 10,
                IssueType.MISSING_VALUES: 11
            }
            actions.sort(key=lambda a: action_order.get(a.issue_type, 99))
            
            # Apply actions to dataframe
            df = df.copy()
            for action in actions:
                try:
                    df = self._apply_action(df, action)
                    all_applied_actions.append({
                        "iteration": iteration,
                        "issue_type": action.issue_type.value,
                        "columns": action.columns,
                        "method": action.method,
                        "status": "success"
                    })
                except Exception as e:
                    print(f"  ✗ Failed: {str(e)}")
                    all_applied_actions.append({
                        "iteration": iteration,
                        "issue_type": action.issue_type.value,
                        "columns": action.columns,
                        "method": action.method,
                        "status": "failed",
                        "error": str(e)
                    })
        
        # Save final processed data
        print(f"\\n{'='*50}")
        print(f"FINAL SAVE: Saving cleaned data...")
        print(f"{'='*50}")
        processed_path = self.file_handler.save_processed_dataframe(file_id, df)
        
        # Get final issue count
        final_issues = self._analyze_dataframe(df)
        
        return PreprocessResponse(
            file_id=file_id,
            original_rows=original_rows,
            processed_rows=len(df),
            applied_actions=all_applied_actions,
            download_url=f"/api/download/{file_id}",
            summary={
                "rows_removed": original_rows - len(df),
                "columns": len(df.columns),
                "actions_applied": len([a for a in all_applied_actions if a["status"] == "success"]),
                "iterations": iteration,
                "remaining_issues": len(final_issues)
            }
        )
    
    def _analyze_dataframe(self, df: pd.DataFrame) -> List[DataIssue]:
        """Analyze a DataFrame and return list of issues (without file I/O)"""
        issues = []
        
        # Check all issue types directly on DataFrame
        issues.extend(self.analyzer._check_missing_values(df))
        issues.extend(self.analyzer._check_duplicates(df))
        issues.extend(self.analyzer._check_outliers(df))
        issues.extend(self.analyzer._check_data_types(df))
        issues.extend(self.analyzer._check_categorical_issues(df))
        issues.extend(self.analyzer._check_constant_features(df))
        issues.extend(self.analyzer._check_correlated_features(df))
        issues.extend(self.analyzer._check_skewness(df))
        issues.extend(self.analyzer._check_high_cardinality(df))
        issues.extend(self.analyzer._check_date_formats(df))
        issues.extend(self.analyzer._check_text_issues(df))
        issues.extend(self.analyzer._check_imbalanced_data(df))
        
        return issues
    
    def _get_recommended_action(self, issue: DataIssue) -> PreprocessAction:
        """Get recommended action for an issue - FIX EVERYTHING"""
        method = None
        parameters = {}
        
        if issue.type == IssueType.MISSING_VALUES:
            method = "mode"  # Works for both categorical and numeric
        elif issue.type == IssueType.DUPLICATES:
            method = "remove"
        elif issue.type == IssueType.OUTLIERS:
            method = "cap"  # Cap to preserve data
        elif issue.type == IssueType.CATEGORICAL_INCONSISTENCIES:
            method = "normalize"
        elif issue.type == IssueType.WRONG_DATE_FORMAT:
            method = "convert"
            parameters = {"format": "%Y-%m-%d"}
        elif issue.type == IssueType.NOISY_TEXT:
            method = "lowercase"
        elif issue.type == IssueType.CONSTANT_VALUES:
            method = "remove"
        elif issue.type == IssueType.SKEWNESS:
            method = "log_transform"
        elif issue.type == IssueType.HIGH_CARDINALITY:
            method = "group_rare"
        elif issue.type == IssueType.CORRELATED_FEATURES:
            method = "remove_correlated"
        elif issue.type == IssueType.INCONSISTENT_TYPES:
            method = "convert"
        elif issue.type == IssueType.IMBALANCED_DATA:
            # Cannot auto-fix imbalanced data (requires sampling/SMOTE)
            print(f"    → No automatic fix available for {issue.type.value}")
            return None
        else:
            print(f"    → No handler for issue type: {issue.type.value}")
            return None
        
        if method is None:
            return None
            
        return PreprocessAction(
            issue_type=issue.type,
            columns=issue.affected_columns,
            method=method,
            parameters=parameters
        )
    
    async def get_processed_file_path(self, file_id: str) -> str:
        """Get the path to processed file"""
        return self.file_handler.get_processed_file_path(file_id)
    
    def _handle_high_cardinality(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        method: str
    ) -> pd.DataFrame:
        """Handle high cardinality columns"""
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == "group_rare":
                # Group categories that appear less than 1% of the time
                threshold = len(df) * 0.01
                value_counts = df[col].value_counts()
                rare_categories = value_counts[value_counts < threshold].index
                if len(rare_categories) > 0:
                    df[col] = df[col].replace(rare_categories, 'Other')
                    print(f"    Column '{col}': Grouped {len(rare_categories)} rare categories into 'Other'")
        
        return df
    
    def _handle_correlated_features(
        self, 
        df: pd.DataFrame, 
        columns: List[str]
    ) -> pd.DataFrame:
        """Handle highly correlated features by removing one from each pair"""
        if len(columns) > 0:
            # Remove the first column from each correlated pair
            cols_to_remove = columns[:len(columns)//2]  # Remove half of correlated features
            df = df.drop(columns=[col for col in cols_to_remove if col in df.columns])
            print(f"    Removed {len(cols_to_remove)} correlated features: {cols_to_remove}")
        
        return df
    
    def _handle_inconsistent_types(
        self, 
        df: pd.DataFrame, 
        columns: List[str]
    ) -> pd.DataFrame:
        """Handle columns with inconsistent data types"""
        for col in columns:
            if col not in df.columns:
                continue
            
            # Check if column has many unique values (high cardinality) - likely categorical
            unique_count = df[col].nunique()
            row_count = len(df)
            
            # If unique values > 50% of rows, it's high cardinality - keep as categorical
            if unique_count / row_count > 0.5:
                df[col] = df[col].astype(str)
                print(f"    Column '{col}': Kept as string (high cardinality: {unique_count} unique values)")
                continue
            
            # Check if column looks numeric (more than 70% numeric values)
            try:
                numeric_converted = pd.to_numeric(df[col], errors='coerce')
                non_null_count = df[col].notna().sum()
                numeric_count = numeric_converted.notna().sum()
                
                if numeric_count / non_null_count > 0.7:  # More than 70% are numeric
                    df[col] = numeric_converted
                    print(f"    Column '{col}': Converted to numeric ({numeric_count}/{non_null_count} values)")
                else:
                    # Mostly non-numeric, keep as string
                    df[col] = df[col].astype(str)
                    print(f"    Column '{col}': Kept as string (not primarily numeric)")
            except:
                # If conversion fails, keep as string
                df[col] = df[col].astype(str)
                print(f"    Column '{col}': Kept as string (conversion failed)")
        
        return df
