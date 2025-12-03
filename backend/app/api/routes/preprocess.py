from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.schemas import PreprocessRequest, PreprocessResponse
from app.services.data_preprocessor import DataPreprocessor

router = APIRouter()
preprocessor = DataPreprocessor()

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
        file_path = await preprocessor.get_processed_file_path(file_id)
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
