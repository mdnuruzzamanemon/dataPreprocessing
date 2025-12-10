from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.schemas import AnalysisResponse
from app.models.database import User, File as DBFile
from app.services.data_analyzer import DataAnalyzer
from app.database import get_db
from app.api.dependencies import get_current_user
import json
import os

router = APIRouter()
analyzer = DataAnalyzer()

@router.get("/analyze/{file_id}", response_model=AnalysisResponse)
async def analyze_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze uploaded file for data quality issues (requires authentication)
    """
    # Verify file belongs to user
    db_file = db.query(DBFile).filter(
        DBFile.file_id == file_id,
        DBFile.user_id == current_user.id
    ).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Load failed columns metadata if it exists
        metadata_dir = "temp/metadata"
        metadata_file = os.path.join(metadata_dir, f"{file_id}_failed_columns.json")
        exclude_skewness_columns = set()
        
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    exclude_skewness_columns = set(data.get('failed_skewness_columns', []))
            except Exception as e:
                print(f"Warning: Could not load failed columns metadata: {e}")
        
        analysis_result = await analyzer.analyze_dataset(file_id, exclude_skewness_columns=exclude_skewness_columns)
        return analysis_result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing file: {str(e)}")

@router.get("/analyze/{file_id}/preview")
async def preview_data(file_id: str, rows: int = 10):
    """
    Get a preview of the dataset
    """
    try:
        preview = await analyzer.get_data_preview(file_id, rows)
        return preview
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting preview: {str(e)}")

@router.get("/analyze/{file_id}/info")
async def get_data_info(file_id: str):
    """
    Get detailed information about the dataset for debugging
    """
    try:
        from app.services.file_handler import FileHandler
        import pandas as pd
        
        file_handler = FileHandler()
        df = file_handler.load_dataframe(file_id)
        
        # Get comprehensive data info
        info = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "null_counts": {col: int(count) for col, count in df.isnull().sum().items() if count > 0},
            "total_nulls": int(df.isnull().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
            "object_columns": df.select_dtypes(include=['object']).columns.tolist(),
            "sample_data": df.head(3).to_dict(orient='records')
        }
        
        return info
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting info: {str(e)}")
