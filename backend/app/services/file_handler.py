from fastapi import UploadFile
import pandas as pd
import numpy as np
import os
from app.core.config import settings
from app.models.schemas import FileInfo
import aiofiles

class FileHandler:
    """Handle file upload, storage, and retrieval"""
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.temp_dir = settings.TEMP_DIR
    
    async def save_uploaded_file(self, file: UploadFile, file_id: str) -> FileInfo:
        """Save uploaded file and return file info"""
        file_ext = os.path.splitext(file.filename)[1].lower()
        file_path = os.path.join(self.upload_dir, f"{file_id}{file_ext}")
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Load data to get info
        df = self._load_dataframe(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return FileInfo(
            file_id=file_id,
            filename=file.filename,
            rows=len(df),
            columns=len(df.columns),
            size=file_size,
            file_type=file_ext[1:]  # Remove dot
        )
    
    def _load_dataframe(self, file_path: str) -> pd.DataFrame:
        """Load DataFrame from file"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Common representations of missing values
        na_values = ['', ' ', 'NA', 'N/A', 'na', 'n/a', 'NULL', 'null', 
                     'NaN', 'nan', 'None', 'none', '-', '--', '?', 'missing',
                     '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', '-NaN', 
                     '-nan', '1.#IND', '1.#QNAN', '<NA>', 'N/A', 'NA', 'NULL', 
                     'NaN', 'n/a', 'nan', 'null']
        
        if file_ext == '.csv':
            # Read CSV with comprehensive NA handling
            df = pd.read_csv(
                file_path, 
                na_values=na_values, 
                keep_default_na=True,
                skipinitialspace=True  # Remove leading spaces
            )
            # Also treat empty strings as NaN after reading
            df = df.replace(r'^\s*$', np.nan, regex=True)
            return df
        elif file_ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path, na_values=na_values, keep_default_na=True)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def load_dataframe(self, file_id: str) -> pd.DataFrame:
        """Load DataFrame by file ID - prefers processed version if available"""
        # Check if processed file exists first
        processed_path = os.path.join(self.temp_dir, f"{file_id}_processed.csv")
        if os.path.exists(processed_path):
            print(f"Loading PROCESSED file: {processed_path}")
            return self._load_dataframe(processed_path)
        
        # Otherwise load original file
        file_path = self._get_file_path(file_id)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_id}")
        print(f"Loading ORIGINAL file: {file_path}")
        return self._load_dataframe(file_path)
    
    def _get_file_path(self, file_id: str) -> str:
        """Get file path by ID"""
        for ext in settings.ALLOWED_EXTENSIONS:
            file_path = os.path.join(self.upload_dir, f"{file_id}{ext}")
            if os.path.exists(file_path):
                return file_path
        raise FileNotFoundError(f"File not found: {file_id}")
    
    async def delete_file(self, file_id: str):
        """Delete file by ID"""
        file_path = self._get_file_path(file_id)
        os.remove(file_path)
        
        # Also delete processed file if exists
        processed_path = os.path.join(self.temp_dir, f"{file_id}_processed.csv")
        if os.path.exists(processed_path):
            os.remove(processed_path)
    
    def save_processed_dataframe(self, file_id: str, df: pd.DataFrame) -> str:
        """Save processed DataFrame and return file path"""
        file_path = os.path.join(self.temp_dir, f"{file_id}_processed.csv")
        
        # Log before saving
        print(f"\n--- SAVING PROCESSED FILE ---")
        print(f"DataFrame shape: {df.shape}")
        print(f"Missing values per column BEFORE save:")
        print(df.isna().sum())
        print(f"Total missing values: {df.isna().sum().sum()}")
        
        # Save with proper NA handling - don't write NaN as string
        df.to_csv(file_path, index=False, na_rep='')
        print(f"Saved to: {file_path}")
        
        # Verify by reading back
        print(f"\n--- VERIFYING SAVED FILE ---")
        df_verify = self._load_dataframe(file_path)
        print(f"Loaded shape: {df_verify.shape}")
        print(f"Missing values per column AFTER save:")
        print(df_verify.isna().sum())
        print(f"Total missing values: {df_verify.isna().sum().sum()}")
        print(f"--- VERIFICATION COMPLETE ---\n")
        
        return file_path
    
    def get_processed_file_path(self, file_id: str) -> str:
        """Get processed file path"""
        file_path = os.path.join(self.temp_dir, f"{file_id}_processed.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Processed file not found: {file_id}")
        return file_path
