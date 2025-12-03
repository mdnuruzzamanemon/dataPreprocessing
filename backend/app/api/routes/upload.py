from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import FileInfo
from app.services.file_handler import FileHandler
from app.core.config import settings
import uuid
import os

router = APIRouter()
file_handler = FileHandler()

@router.post("/upload", response_model=FileInfo)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a CSV or Excel file for analysis
    """
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    
    try:
        # Save and process file
        file_info = await file_handler.save_uploaded_file(file, file_id)
        return file_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.delete("/upload/{file_id}")
async def delete_file(file_id: str):
    """
    Delete an uploaded file
    """
    try:
        await file_handler.delete_file(file_id)
        return {"message": "File deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
