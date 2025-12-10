from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.schemas import FileInfo
from app.models.database import User, File as DBFile
from app.services.file_handler import FileHandler
from app.core.config import settings
from app.database import get_db
from app.api.dependencies import get_current_user
import uuid
import os

router = APIRouter()
file_handler = FileHandler()

@router.post("/upload", response_model=FileInfo)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a CSV or Excel file for analysis (requires authentication)
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
        
        # Save file metadata to database
        db_file = DBFile(
            user_id=current_user.id,
            file_id=file_id,
            filename=file.filename,
            file_path=os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_ext}"),
            file_size=len(contents),
            file_type=file_ext[1:],  # Remove the dot
            status="uploaded"
        )
        db.add(db_file)
        db.commit()
        
        return file_info
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.delete("/upload/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an uploaded file (requires authentication)
    """
    # Verify file belongs to user
    db_file = db.query(DBFile).filter(
        DBFile.file_id == file_id,
        DBFile.user_id == current_user.id
    ).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        await file_handler.delete_file(file_id)
        db.delete(db_file)
        db.commit()
        return {"message": "File deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
