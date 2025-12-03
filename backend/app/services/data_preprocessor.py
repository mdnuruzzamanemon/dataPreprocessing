import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler, RobustScaler
from typing import List, Dict, Any
from app.models.schemas import PreprocessAction, PreprocessResponse, IssueType, DataIssue
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
        df = self.file_handler.load_dataframe(file_id)
        original_rows = len(df)
        applied_actions = []
        
        # Apply each action
        for action in actions:
            try:
                df = self._apply_action(df, action)
                applied_actions.append({
                    "issue_type": action.issue_type.value,
                    "columns": action.columns,
                    "method": action.method,
                    "status": "success"
                })
            except Exception as e:
                applied_actions.append({
                    "issue_type": action.issue_type.value,
                    "columns": action.columns,
                    "method": action.method,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Save processed data
        processed_path = self.file_handler.save_processed_dataframe(file_id, df)
        
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
        else:
            raise ValueError(f"Unsupported issue type: {issue_type}")
    
    def _handle_missing_values(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        method: str
    ) -> pd.DataFrame:
        """Handle missing values"""
        for col in columns:
            if col not in df.columns:
                continue
            
            if method == "mean":
                df[col].fillna(df[col].mean(), inplace=True)
            elif method == "median":
                df[col].fillna(df[col].median(), inplace=True)
            elif method == "mode":
                df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else df[col], inplace=True)
            elif method == "forward_fill":
                df[col].fillna(method='ffill', inplace=True)
            elif method == "backward_fill":
                df[col].fillna(method='bfill', inplace=True)
            elif method == "drop":
                df.dropna(subset=[col], inplace=True)
        
        return df
    
    def _handle_duplicates(self, df: pd.DataFrame, method: str) -> pd.DataFrame:
        """Handle duplicate rows"""
        if method == "remove":
            df.drop_duplicates(inplace=True)
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
            
            if method == "remove":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            
            elif method == "cap":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
            
            elif method == "log_transform":
                # Add small constant to avoid log(0)
                df[col] = np.log1p(df[col] - df[col].min() + 1)
        
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
                df[col] = df[col].str.lower().str.strip()
            
            elif method == "label_encode":
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
            
            elif method == "one_hot":
                dummies = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df.drop(col, axis=1), dummies], axis=1)
        
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
                df[col] = df[col].str.lower()
            
            elif method == "remove_punctuation":
                df[col] = df[col].str.replace(r'[^\w\s]', '', regex=True)
            
            elif method == "remove_stopwords":
                # Simple stopword removal (can be enhanced with NLTK)
                stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
                df[col] = df[col].apply(
                    lambda x: ' '.join([word for word in str(x).split() if word.lower() not in stopwords])
                )
        
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
        """Automatically fix all detected issues with recommended actions"""
        # First, analyze the data
        analysis = await self.analyzer.analyze_dataset(file_id)
        
        # Generate actions for each issue
        actions = []
        for issue in analysis.issues:
            action = self._get_recommended_action(issue)
            if action:
                actions.append(action)
        
        # Apply all actions
        return await self.preprocess_dataset(file_id, actions)
    
    def _get_recommended_action(self, issue: DataIssue) -> PreprocessAction:
        """Get recommended action for an issue"""
        action_map = {
            IssueType.MISSING_VALUES: ("median", {}),
            IssueType.DUPLICATES: ("remove", {}),
            IssueType.OUTLIERS: ("cap", {}),
            IssueType.CATEGORICAL_INCONSISTENCIES: ("normalize", {}),
            IssueType.WRONG_DATE_FORMAT: ("convert", {"format": "%Y-%m-%d"}),
            IssueType.NOISY_TEXT: ("lowercase", {}),
            IssueType.CONSTANT_VALUES: ("remove", {}),
            IssueType.SKEWNESS: ("log_transform", {}),
        }
        
        if issue.type in action_map:
            method, parameters = action_map[issue.type]
            return PreprocessAction(
                issue_type=issue.type,
                columns=issue.affected_columns,
                method=method,
                parameters=parameters
            )
        return None
    
    async def get_processed_file_path(self, file_id: str) -> str:
        """Get the path to processed file"""
        return self.file_handler.get_processed_file_path(file_id)
