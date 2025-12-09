from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.models.schemas import PreprocessRequest, PreprocessResponse
from app.services.data_preprocessor import DataPreprocessor

router = APIRouter()
preprocessor = DataPreprocessor()

class ImbalancedDataRequest(BaseModel):
    target_column: str
    method: str  # smote, oversample, or undersample

@router.post("/preprocess/{file_id}", response_model=PreprocessResponse)
async def preprocess_file(file_id: str, request: PreprocessRequest):
    """
    Apply preprocessing actions to the dataset
    """
    try:
        result = await preprocessor.preprocess_dataset(file_id, request.actions)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error preprocessing file: {str(e)}")

@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """
    Download the processed dataset
    """
    try:
        # get_processed_file_path is synchronous, don't await it
        file_path = preprocessor.file_handler.get_processed_file_path(file_id)
        return FileResponse(
            path=file_path,
            media_type="application/octet-stream",
            filename=f"processed_{file_id}.csv"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Processed file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

@router.post("/preprocess/{file_id}/fix-all")
async def fix_all_issues(file_id: str):
    """
    Automatically apply recommended fixes for all detected issues
    """
    try:
        result = await preprocessor.fix_all_issues(file_id)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fixing issues: {str(e)}")

@router.post("/preprocess/{file_id}/fix-imbalanced")
async def fix_imbalanced_data(file_id: str, request: ImbalancedDataRequest):
    """
    Fix imbalanced data using selected sampling method, then auto-fix any new issues
    """
    try:
        print(f"\n=== FIXING IMBALANCED DATA ===")
        print(f"Method: {request.method}, Target: {request.target_column}")
        
        # Load the DataFrame (NOT async)
        df = preprocessor.file_handler.load_dataframe(file_id)
        original_rows = len(df)
        
        # Apply imbalanced data handling
        df_processed = preprocessor._handle_imbalanced_data(
            df, 
            request.target_column, 
            request.method
        )
        
        # Save the processed file (NOT async) - returns PATH, not file_id!
        processed_path = preprocessor.file_handler.save_processed_dataframe(
            file_id,
            df_processed
        )
        
        print(f"✓ Imbalanced data fixed: {original_rows} → {len(df_processed)} rows")
        print(f"\n=== AUTO-FIXING NEW ISSUES CREATED BY SAMPLING ===")
        
        # Automatically run fix_all_issues to clean up any new issues created by sampling
        # (e.g., duplicates, outliers, skewness from synthetic data)
        auto_fix_result = await preprocessor.fix_all_issues(file_id)
        
        print(f"✓ Auto-fix complete: {auto_fix_result.summary['actions_applied']} actions applied")
        print(f"=== IMBALANCED DATA FIX COMPLETE ===\n")
        
        return {
            "file_id": file_id,
            "status": "success",
            "message": f"Applied {request.method} and auto-fixed resulting issues",
            "original_rows": original_rows,
            "processed_rows": auto_fix_result.processed_rows,
            "actions_applied": auto_fix_result.summary['actions_applied'],
            "remaining_issues": auto_fix_result.summary['remaining_issues']
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fixing imbalanced data: {str(e)}")
