from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalysisResponse
from app.services.data_analyzer import DataAnalyzer

router = APIRouter()
analyzer = DataAnalyzer()

@router.get("/analyze/{file_id}", response_model=AnalysisResponse)
async def analyze_file(file_id: str):
    """
    Analyze uploaded file for data quality issues
    """
    try:
        analysis_result = await analyzer.analyze_dataset(file_id)
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
