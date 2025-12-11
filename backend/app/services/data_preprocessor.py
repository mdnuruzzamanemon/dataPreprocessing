import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler, RobustScaler
from typing import List, Dict, Any
from app.models.schemas import PreprocessAction, PreprocessResponse, IssueType, DataIssue, IssueSeverity
from app.services.file_handler import FileHandler
from app.services.data_analyzer import DataAnalyzer
import re
import json
import os

class DataPreprocessor:
    """Apply preprocessing transformations to datasets"""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.analyzer = DataAnalyzer()
        self.metadata_dir = "temp/metadata"
        os.makedirs(self.metadata_dir, exist_ok=True)
    
    async def preprocess_dataset(
        self, 
        file_id: str, 
        actions: List[PreprocessAction]
    ) -> PreprocessResponse:
        """Apply user-selected preprocessing actions to dataset"""
        print(f"\n=== APPLYING SELECTED ACTIONS ===")
        print(f"File ID: {file_id}")
        print(f"Number of actions: {len(actions)}")
        
        # Load failed columns metadata
        failed_skewness_columns = self._load_failed_columns(file_id)
        
        df = self.file_handler.load_dataframe(file_id)
        df = df.copy()
        original_rows = len(df)
        print(f"Original rows: {original_rows}")
        applied_actions = []
        
        # Apply each selected action
        for action in actions:
            try:
                print(f"\n→ Applying {action.issue_type.value} fix on {len(action.columns)} columns using '{action.method}'")
                
                # Handle skewness with failed column filtering
                if action.issue_type == IssueType.SKEWNESS:
                    # Filter out columns that have already failed
                    fixable_columns = [col for col in action.columns if col not in failed_skewness_columns]
                    if not fixable_columns:
                        print(f"    → Skipping - all columns previously failed transformation")
                        applied_actions.append({
                            "issue_type": action.issue_type.value,
                            "columns": action.columns,
                            "method": action.method,
                            "status": "skipped",
                            "reason": "all_columns_unfixable"
                        })
                        continue
                    action.columns = fixable_columns
                
                df_before = df.copy()
                df = self._apply_action(df, action)
                
                # Check if skewness transformation actually worked
                if action.issue_type == IssueType.SKEWNESS:
                    if df.equals(df_before):
                        print(f"    ⚠️ Skewness transformation failed for {action.columns}")
                        print(f"    → Removing unfixable columns: {action.columns}")
                        
                        # Drop unfixable columns
                        df = df.drop(columns=action.columns, errors='ignore')
                        
                        # Save to metadata
                        failed_skewness_columns.update(action.columns)
                        self._save_failed_columns(file_id, failed_skewness_columns)
                        
                        applied_actions.append({
                            "issue_type": action.issue_type.value,
                            "columns": action.columns,
                            "method": "remove_column",
                            "status": "removed",
                            "reason": "transformation_ineffective"
                        })
                        continue
                
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
        processed_path = self.file_handler.save_processed_dataframe(file_id, df)
        
        # Update file status to 'processed' in database
        self._update_file_status(file_id, 'processed')
        
        # Re-analyze to get remaining issues (full analysis for frontend)
        remaining_issues_analysis = self._analyze_dataframe(df, exclude_skewness_columns=failed_skewness_columns)
        remaining_issues_count = len(remaining_issues_analysis)
        
        print(f"\n✅ Selected actions applied successfully")
        print(f"   Remaining issues: {remaining_issues_count}")
        print(f"=== PREPROCESSING COMPLETE ===\n")
        
        # Create full AnalysisResponse for frontend (same format as /api/analyze)
        from app.models.schemas import AnalysisResponse, FileInfo
        import os
        
        file_path = self.file_handler._get_file_path(file_id)
        if not os.path.exists(file_path):
            # Use processed file path
            file_path = processed_path
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
        
        # Create summary for analysis
        analysis_summary = {}
        for issue in remaining_issues_analysis:
            issue_type = issue.type.value
            if issue_type in analysis_summary:
                analysis_summary[issue_type] += 1
            else:
                analysis_summary[issue_type] = 1
        
        # Create full AnalysisResponse
        analysis_response = AnalysisResponse(
            file_id=file_id,
            file_info=file_info,
            issues=remaining_issues_analysis,
            total_issues=remaining_issues_count,
            summary=analysis_summary
        )
        
        return PreprocessResponse(
            file_id=file_id,
            original_rows=original_rows,
            processed_rows=len(df),
            applied_actions=applied_actions,
            download_url=f"/api/download/{file_id}",
            summary={
                "rows_removed": original_rows - len(df),
                "columns": len(df.columns),
                "actions_applied": len([a for a in applied_actions if a["status"] == "success"]),
                "remaining_issues": remaining_issues_count
            },
            analysis=analysis_response  # Full analysis for frontend to update UI
        )
    
    def _normalize_method_name(self, method: str, issue_type: IssueType) -> str:
        """Normalize frontend method names to backend format"""
        method_lower = method.lower().replace('_', ' ').replace('(', '').replace(')', '')
        
        # Handle missing values methods
        if issue_type == IssueType.MISSING_VALUES:
            if 'mean' in method_lower:
                return 'mean'
            elif 'median' in method_lower:
                return 'median'
            elif 'mode' in method_lower:
                return 'mode'
            elif 'forward' in method_lower:
                return 'forward_fill'
            elif 'backward' in method_lower:
                return 'backward_fill'
            elif 'drop' in method_lower:
                return 'drop'
        
        # Handle duplicates
        elif issue_type == IssueType.DUPLICATES:
            return 'remove'
        
        # Handle outliers methods
        elif issue_type == IssueType.OUTLIERS:
            if 'cap' in method_lower or 'iqr' in method_lower:
                return 'cap'
            elif 'remove' in method_lower:
                return 'remove'
            elif 'log' in method_lower:
                return 'log'
        
        # Handle skewness methods
        elif issue_type == IssueType.SKEWNESS:
            if 'log' in method_lower:
                return 'log'
            elif 'sqrt' in method_lower or 'square root' in method_lower:
                return 'sqrt'
            elif 'box' in method_lower or 'cox' in method_lower:
                return 'box_cox'
        
        # Handle high cardinality
        elif issue_type == IssueType.HIGH_CARDINALITY:
            if 'group' in method_lower or 'rare' in method_lower:
                return 'group_rare'
            elif 'target' in method_lower:
                return 'target_encoding'
            elif 'remove' in method_lower:
                return 'remove'
        
        # Handle categorical inconsistencies
        elif issue_type == IssueType.CATEGORICAL_INCONSISTENCIES:
            if 'normalize' in method_lower or 'naming' in method_lower:
                return 'normalize'
            elif 'label' in method_lower:
                return 'label_encode'  # Match _handle_categorical method name
            elif 'one hot' in method_lower or 'onehot' in method_lower:
                return 'one_hot'
        
        # Handle inconsistent types
        elif issue_type == IssueType.INCONSISTENT_TYPES:
            return 'convert'
        
        # Handle constant values
        elif issue_type == IssueType.CONSTANT_VALUES:
            return 'remove'
        
        # Handle correlated features
        elif issue_type == IssueType.CORRELATED_FEATURES:
            if 'pca' in method_lower:
                return 'pca'
            else:
                return 'remove'
        
        # Handle date formats
        elif issue_type == IssueType.WRONG_DATE_FORMAT:
            if 'extract' in method_lower or 'component' in method_lower:
                return 'extract_components'
            else:
                return 'standardize'
        
        # Handle noisy text
        elif issue_type == IssueType.NOISY_TEXT:
            if 'lowercase' in method_lower:
                return 'lowercase'
            elif 'punctuation' in method_lower:
                return 'remove_punctuation'
            elif 'stopword' in method_lower:
                return 'remove_stopwords'
        
        # Handle imbalanced data
        elif issue_type == IssueType.IMBALANCED_DATA:
            if 'smote' in method_lower:
                return 'smote'
            elif 'undersample' in method_lower:
                return 'undersample'
            elif 'oversample' in method_lower:
                return 'oversample'
        
        # Default: return as-is
        return method
    
    def _apply_action(self, df: pd.DataFrame, action: PreprocessAction) -> pd.DataFrame:
        """Apply a single preprocessing action"""
        issue_type = action.issue_type
        columns = action.columns
        method = self._normalize_method_name(action.method, issue_type)
        
        print(f"  → Applying {issue_type.value} fix on {len(columns)} columns using method '{method}'")
        
        if issue_type == IssueType.MISSING_VALUES:
            return self._handle_missing_values(df, columns, method)
        elif issue_type == IssueType.DUPLICATES:
            return self._handle_duplicates(df, method)
        elif issue_type == IssueType.OUTLIERS:
            print(f"    Calling _handle_outliers with columns: {columns}")
            result = self._handle_outliers(df, columns, method)
            print(f"    Outlier handler returned DataFrame with {len(result)} rows")
            return result
        elif issue_type == IssueType.CATEGORICAL_INCONSISTENCIES:
            return self._handle_categorical(df, columns, method)
        elif issue_type == IssueType.WRONG_DATE_FORMAT:
            return self._handle_dates(df, columns, method, action.parameters)
        elif issue_type == IssueType.NOISY_TEXT:
            return self._handle_text(df, columns, method)
        elif issue_type == IssueType.CONSTANT_VALUES:
            return self._remove_columns(df, columns)
        elif issue_type == IssueType.SKEWNESS:
            print(f"    Calling _handle_skewness with columns: {columns}")
            result = self._handle_skewness(df, columns, method)
            print(f"    Skewness handler returned DataFrame")
            return result
        elif issue_type == IssueType.HIGH_CARDINALITY:
            return self._handle_high_cardinality(df, columns, method)
        elif issue_type == IssueType.CORRELATED_FEATURES:
            return self._handle_correlated_features(df, columns)
        elif issue_type == IssueType.INCONSISTENT_TYPES:
            return self._handle_inconsistent_types(df, columns)
        elif issue_type == IssueType.IMBALANCED_DATA:
            target_column = action.parameters.get("target_column", columns[0] if columns else None)
            print(f"    → Imbalanced data fix:")
            print(f"       Target column: {target_column}")
            print(f"       Method: {method}")
            print(f"       Columns from action: {columns}")
            print(f"       Parameters: {action.parameters}")
            
            if not target_column:
                print(f"    ⚠️  ERROR: No target column specified!")
                return df
            
            result = self._handle_imbalanced_data(df, target_column, method)
            print(f"    ✓ Imbalanced data handler returned DataFrame with {len(result)} rows")
            return result
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
            
            # Auto-adjust method for non-numeric columns
            actual_method = method
            if method in ["mean", "median"] and not pd.api.types.is_numeric_dtype(df[col]):
                actual_method = "mode"
                print(f"    ⚠️  Auto-adjusted: '{method}' → 'mode' (column is non-numeric)")
            
            if actual_method == "mean":
                if pd.api.types.is_numeric_dtype(df[col]):
                    mean_val = df[col].mean()
                    df[col] = df[col].fillna(mean_val)
                    print(f"    Filled with mean: {mean_val}")
                else:
                    print(f"    WARNING: Cannot use mean on non-numeric column, skipping")
                    
            elif actual_method == "median":
                if pd.api.types.is_numeric_dtype(df[col]):
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                    print(f"    Filled with median: {median_val}")
                else:
                    print(f"    WARNING: Cannot use median on non-numeric column, skipping")
                    
            elif actual_method == "mode":
                mode_val = df[col].mode()
                if not mode_val.empty:
                    df[col] = df[col].fillna(mode_val[0])
                    print(f"    Filled with mode: {mode_val[0]}")
                else:
                    print(f"    WARNING: No mode found, skipping")
                    
            elif actual_method == "forward_fill":
                df[col] = df[col].ffill()
                print(f"    Applied forward fill")
                
            elif actual_method == "backward_fill":
                df[col] = df[col].bfill()
                print(f"    Applied backward fill")
                
            elif actual_method == "drop":
                rows_before = len(df)
                df = df.dropna(subset=[col])
                rows_dropped = rows_before - len(df)
                print(f"    Dropped {rows_dropped} rows")
            
            missing_after = df[col].isna().sum()
            fixed_count = missing_before - missing_after
            print(f"    After {actual_method}: {missing_after} missing values (fixed {fixed_count})")
            
            # Only warn if we actually tried to fix it and failed
            if missing_after > 0 and actual_method not in ["forward_fill", "backward_fill"] and fixed_count == 0:
                print(f"    WARNING: Still has {missing_after} missing values after {actual_method}!")
        
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
                print(f"    Column '{col}' not found")
                continue
            
            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(df[col]):
                print(f"    Skipping non-numeric column '{col}'")
                continue
            
            if method == "remove":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers_before = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                print(f"    Column '{col}': Removed {outliers_before} outliers (rows: {len(df)})")
            
            elif method == "cap":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                # Use SAME threshold as detection (1.5*IQR) or tighter
                # Cap at 1.5*IQR to match detection threshold
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers_before = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                
                # Actually cap the values
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                
                # Verify outliers are gone
                outliers_after = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                print(f"    Column '{col}': Capped {outliers_before} outliers → {outliers_after} remaining")
            
            elif method == "log_transform":
                # Add small constant to avoid log(0)
                min_val = df[col].min()
                if min_val <= 0:
                    df[col] = np.log1p(df[col] - min_val + 1)
                else:
                    df[col] = np.log1p(df[col])
                print(f"    Column '{col}': Applied log transform to reduce outliers")
        
        return df
    
    def _handle_imbalanced_data(
        self,
        df: pd.DataFrame,
        target_column: str,
        method: str
    ) -> pd.DataFrame:
        """Handle imbalanced data using sampling techniques"""
        if target_column not in df.columns:
            print(f"    Target column '{target_column}' not found")
            return df
        
        try:
            from imblearn.over_sampling import SMOTE, RandomOverSampler
            from imblearn.under_sampling import RandomUnderSampler
            from sklearn.model_selection import train_test_split
            
            # Check for missing values in target column
            missing_in_target = df[target_column].isna().sum()
            if missing_in_target > 0:
                print(f"    ⚠️  Target column '{target_column}' has {missing_in_target} missing values")
                print(f"    → Dropping rows with missing target values")
                df = df.dropna(subset=[target_column])
                print(f"    → Rows after dropping: {len(df)}")
            
            # Separate features and target
            X = df.drop(columns=[target_column])
            y = df[target_column]
            
            # Convert categorical features to numeric for SMOTE
            X_numeric = pd.get_dummies(X, drop_first=True)
            
            if method == "smote":
                # Check class distribution
                class_counts = y.value_counts()
                min_samples = class_counts.min()
                print(f"    Class distribution: {class_counts.to_dict()}")
                print(f"    Minimum samples in any class: {min_samples}")
                
                # SMOTE requires at least 2 samples in minority class
                # and k_neighbors must be less than minority class size
                if min_samples < 2:
                    print(f"    ⚠️  SMOTE requires at least 2 samples per class, found {min_samples}")
                    print(f"    → Falling back to RandomOverSampler")
                    sampler = RandomOverSampler(random_state=42)
                else:
                    # Adjust k_neighbors based on minority class size
                    # Default k_neighbors=5, but must be < minority class size
                    k_neighbors = min(5, min_samples - 1)
                    print(f"    Using k_neighbors={k_neighbors} for SMOTE")
                    sampler = SMOTE(random_state=42, k_neighbors=k_neighbors)
                
                X_resampled, y_resampled = sampler.fit_resample(X_numeric, y)
                print(f"    ✓ Applied SMOTE: {len(df)} → {len(y_resampled)} rows")
            elif method == "oversample":
                sampler = RandomOverSampler(random_state=42)
                X_resampled, y_resampled = sampler.fit_resample(X_numeric, y)
                print(f"    ✓ Applied Random Oversampling: {len(df)} → {len(y_resampled)} rows")
            elif method == "undersample":
                sampler = RandomUnderSampler(random_state=42)
                X_resampled, y_resampled = sampler.fit_resample(X_numeric, y)
                print(f"    ✓ Applied Random Undersampling: {len(df)} → {len(y_resampled)} rows")
            else:
                print(f"    Unknown method: {method}")
                return df
            
            # Reconstruct dataframe
            df_resampled = pd.DataFrame(X_resampled, columns=X_numeric.columns)
            df_resampled[target_column] = y_resampled
            return df_resampled
            
        except ImportError:
            print(f"    imbalanced-learn not installed. Install with: pip install imbalanced-learn")
            return df
        except Exception as e:
            print(f"    Failed to apply {method}: {str(e)}")
            import traceback
            traceback.print_exc()
            return df
    
    def _handle_categorical(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        method: str
    ) -> pd.DataFrame:
        """Handle categorical data issues"""
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
                print(f"    Column '{col}' not found")
                continue
            
            # Skip non-numeric columns
            if not pd.api.types.is_numeric_dtype(df[col]):
                print(f"    Skipping non-numeric column '{col}'")
                continue
            
            # Calculate skewness before
            skew_before = df[col].skew()
            unique_vals = df[col].nunique()
            col_min, col_max = df[col].min(), df[col].max()
            variation = col_max - col_min
            
            print(f"    Column '{col}': Original skewness = {skew_before:.2f}, unique values = {unique_vals}, variation = {variation:.4f}")
            
            # Skip if column has too few unique values OR insufficient variation
            if unique_vals < 5:
                print(f"    Column '{col}': Too few unique values ({unique_vals}), skipping transform")
                continue
            
            if variation < 0.01:
                print(f"    Column '{col}': Insufficient variation ({variation:.4f}), skipping transform")
                continue
            
            # Store original column to restore if transform doesn't improve skewness
            original_col = df[col].copy()
            original_skew = abs(skew_before)
            
            # Always try log transform first
            min_val = df[col].min()
            if min_val <= 0:
                df[col] = np.log1p(df[col] - min_val + 1)
            else:
                df[col] = np.log1p(df[col])
            
            # Check if log transform created constant/near-constant column
            log_variation = df[col].max() - df[col].min()
            if log_variation < 0.01:
                print(f"    Column '{col}': Log transform created constant column, restoring original")
                df[col] = original_col
                continue
                
            skew_after_log = df[col].skew()
            print(f"    Column '{col}': After log transform = {skew_after_log:.2f}")
            
            # If log transform didn't improve skewness significantly, restore and skip
            if abs(skew_after_log) >= original_skew * 0.90:  # Less than 10% improvement
                print(f"    Column '{col}': Log transform didn't improve skewness enough ({abs(skew_after_log):.2f} vs {original_skew:.2f}), restoring original")
                df[col] = original_col
                continue
            
            # If still significantly skewed, try box-cox
            if abs(skew_after_log) > 0.9:  # Slightly lower threshold for box-cox attempt
                try:
                    from scipy import stats
                    # Box-Cox requires positive values and variation
                    min_val_bc = df[col].min()
                    max_val_bc = df[col].max()
                    
                    # Check if there's enough variation for box-cox
                    if max_val_bc - min_val_bc < 0.01:
                        print(f"    Column '{col}': Insufficient variation for box-cox, keeping log transform")
                        continue
                    
                    if min_val_bc <= 0:
                        df[col] = df[col] - min_val_bc + 1
                    df[col] = stats.boxcox(df[col])[0]
                    skew_final = df[col].skew()
                    print(f"    Column '{col}': After box-cox = {skew_final:.2f} ✓")
                except Exception as e:
                    print(f"    Column '{col}': Box-cox failed: {str(e)[:100]}, keeping log transform")
            else:
                print(f"    Column '{col}': Log transform sufficient ✓")
        
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
        
        # Load previously failed skewness columns for this file
        failed_skewness_columns = self._load_failed_columns(file_id)
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\\n{'='*50}")
            print(f"ITERATION {iteration}: Checking for issues...")
            print(f"{'='*50}")
            
            # Analyze current DataFrame state directly
            issues = self._analyze_dataframe(df, exclude_skewness_columns=failed_skewness_columns)
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
                    # Skip skewness columns that have already failed transformation
                    if action.issue_type == IssueType.SKEWNESS:
                        # Filter out columns that already failed
                        fixable_columns = [col for col in action.columns if col not in failed_skewness_columns]
                        if not fixable_columns:
                            print(f"    → Skipping skewness fix - all columns previously failed transformation")
                            continue
                        # Update action to only include fixable columns
                        action.columns = fixable_columns
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
                IssueType.MISSING_VALUES: 11,
                # Note: IMBALANCED_DATA is intentionally excluded from auto-fix
            }
            actions.sort(key=lambda a: action_order.get(a.issue_type, 99))
            
            # Apply actions to dataframe
            df = df.copy()
            for action in actions:
                try:
                    df_before = df.copy()
                    df = self._apply_action(df, action)
                    
                    # Check if skewness action actually changed the data
                    if action.issue_type == IssueType.SKEWNESS:
                        # If DataFrame didn't change, transformation failed
                        if df.equals(df_before):
                            print(f"    ⚠️ Skewness transformation failed for {action.columns}")
                            print(f"    → Removing unfixable columns: {action.columns}")
                            
                            # Drop the unfixable columns from the dataset
                            df = df.drop(columns=action.columns, errors='ignore')
                            
                            # Track as failed for metadata
                            failed_skewness_columns.update(action.columns)
                            self._save_failed_columns(file_id, failed_skewness_columns)
                            
                            all_applied_actions.append({
                                "iteration": iteration,
                                "issue_type": action.issue_type.value,
                                "columns": action.columns,
                                "method": "remove_column",
                                "status": "removed",
                                "reason": "transformation_ineffective"
                            })
                            continue
                    
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
        
        # Get final issue count and check for imbalanced data (exclude failed skewness columns)
        final_issues = self._analyze_dataframe(df, exclude_skewness_columns=failed_skewness_columns)
        has_imbalanced_data = any(issue.type == IssueType.IMBALANCED_DATA for issue in final_issues)
        imbalanced_columns = None
        if has_imbalanced_data:
            imbalanced_issue = next(issue for issue in final_issues if issue.type == IssueType.IMBALANCED_DATA)
            imbalanced_columns = imbalanced_issue.affected_columns
        
        # Update file status to 'processed' in database
        self._update_file_status(file_id, 'processed')
        
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
                "remaining_issues": len(final_issues),
                "has_imbalanced_data": has_imbalanced_data,
                "imbalanced_columns": imbalanced_columns if has_imbalanced_data else []
            }
        )
    
    def _load_failed_columns(self, file_id: str) -> set:
        """Load previously failed skewness columns for this file"""
        metadata_file = os.path.join(self.metadata_dir, f"{file_id}_failed_columns.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    failed_cols = set(data.get('failed_skewness_columns', []))
                    if failed_cols:
                        print(f"\n📋 Loaded {len(failed_cols)} previously failed skewness columns: {failed_cols}")
                    return failed_cols
            except Exception as e:
                print(f"Warning: Could not load failed columns metadata: {e}")
        return set()
    
    def _save_failed_columns(self, file_id: str, failed_columns: set):
        """Save failed skewness columns to persist across sessions"""
        metadata_file = os.path.join(self.metadata_dir, f"{file_id}_failed_columns.json")
        try:
            with open(metadata_file, 'w') as f:
                json.dump({
                    'failed_skewness_columns': list(failed_columns)
                }, f)
            print(f"💾 Saved {len(failed_columns)} failed columns to metadata")
        except Exception as e:
            print(f"Warning: Could not save failed columns metadata: {e}")
    
    def _analyze_dataframe(self, df: pd.DataFrame, exclude_skewness_columns: set = None) -> List[DataIssue]:
        """Analyze a DataFrame and return list of issues (without file I/O)"""
        issues = []
        
        # Check all issue types directly on DataFrame
        outlier_issues = self.analyzer._check_outliers(df)
        if outlier_issues:
            print(f"    [DETECTION] Found {len(outlier_issues[0].affected_columns)} columns with outliers")
        issues.extend(outlier_issues)
        
        skewness_issues = self.analyzer._check_skewness(df)
        if skewness_issues:
            # Filter out columns that have been marked as unfixable
            if exclude_skewness_columns:
                for issue in skewness_issues:
                    # Remove failed columns from affected_columns
                    issue.affected_columns = [col for col in issue.affected_columns if col not in exclude_skewness_columns]
                    # Update details to match filtered columns
                    if hasattr(issue, 'details') and isinstance(issue.details, dict):
                        issue.details = {k: v for k, v in issue.details.items() if k not in exclude_skewness_columns}
                    # Update count
                    issue.count = len(issue.affected_columns)
                    # Update description
                    if issue.count > 0:
                        issue.description = f"Found {issue.count} columns with skewed distributions"
                # Only add issue if there are still affected columns
                skewness_issues = [issue for issue in skewness_issues if len(issue.affected_columns) > 0]
            print(f"    [DETECTION] Found {len(skewness_issues[0].affected_columns) if skewness_issues else 0} columns with skewness (after excluding unfixable)")
        issues.extend(skewness_issues)
        
        issues.extend(self.analyzer._check_missing_values(df))
        issues.extend(self.analyzer._check_duplicates(df))
        issues.extend(self.analyzer._check_data_types(df))
        issues.extend(self.analyzer._check_categorical_issues(df))
        issues.extend(self.analyzer._check_constant_features(df))
        issues.extend(self.analyzer._check_correlated_features(df))
        # Skewness already checked above - don't check twice!
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
            method = "box_cox"  # Use box-cox for better skewness reduction
        elif issue.type == IssueType.HIGH_CARDINALITY:
            method = "group_rare"
        elif issue.type == IssueType.CORRELATED_FEATURES:
            method = "remove_correlated"
        elif issue.type == IssueType.INCONSISTENT_TYPES:
            method = "convert"
        elif issue.type == IssueType.IMBALANCED_DATA:
            # SKIP auto-fix for imbalanced data - user must select method via popup
            print(f"    → Skipping auto-fix for imbalanced data - requires user selection")
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
    
    def _update_file_status(self, file_id: str, status: str):
        """Update file status in database"""
        try:
            from app.models.database import File as DBFile
            from app.database import get_db
            
            db = next(get_db())
            try:
                db_file = db.query(DBFile).filter(DBFile.file_id == file_id).first()
                if db_file:
                    db_file.status = status
                    db.commit()
                    print(f"✓ Updated file status to '{status}' in database")
            finally:
                db.close()
        except Exception as e:
            print(f"⚠️  Failed to update file status: {e}")
