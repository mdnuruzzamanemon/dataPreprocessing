from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.database import User, File as DBFile
from app.database import get_db
from app.api.dependencies import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/files", tags=["files"])

class FileResponse(BaseModel):
    id: str
    file_id: str
    filename: str
    file_size: int
    file_type: str
    status: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[FileResponse])
async def get_user_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all files for the current user"""
    files = db.query(DBFile).filter(
        DBFile.user_id == current_user.id
    ).order_by(DBFile.uploaded_at.desc()).all()
    
    return [
        FileResponse(
            id=str(file.id),
            file_id=file.file_id,
            filename=file.filename,
            file_size=file.file_size,
            file_type=file.file_type,
            status=file.status,
            uploaded_at=file.uploaded_at
        )
        for file in files
    ]

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a file"""
    import os
    from app.services.file_handler import FileHandler
    
    # Find file in database
    db_file = db.query(DBFile).filter(
        DBFile.file_id == file_id,
        DBFile.user_id == current_user.id
    ).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete physical file
    file_handler = FileHandler()
    try:
        file_path = file_handler.get_file_path(file_id)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete processed file if exists
        processed_path = file_handler.get_processed_file_path(file_id)
        if os.path.exists(processed_path):
            os.remove(processed_path)
    except Exception as e:
        print(f"Error deleting physical file: {e}")
    
    # Delete from database
    db.delete(db_file)
    db.commit()
    
    return {"message": "File deleted successfully"}
