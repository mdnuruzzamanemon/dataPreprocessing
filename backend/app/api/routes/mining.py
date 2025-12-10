from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.database import User, File as DBFile
from app.database import get_db
from app.api.dependencies import get_current_user
from app.services.data_mining import DataMiningService
from app.services.file_handler import FileHandler
import os

router = APIRouter(prefix="/api/mining", tags=["data-mining"])


class MiningRequest(BaseModel):
    file_id: str
    analytics_type: str  # correlation, clustering, classification, regression, association, descriptive
    columns: List[str]
    parameters: Optional[Dict[str, Any]] = {}


class MiningResponse(BaseModel):
    analytics_type: str
    results: Dict[str, Any]
    columns_used: List[str]


@router.get("/columns/{file_id}")
async def get_file_columns(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get column information for a file"""
    # Verify file ownership
    db_file = db.query(DBFile).filter(
        DBFile.file_id == file_id,
        DBFile.user_id == current_user.id
    ).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get file path
    file_handler = FileHandler()
    file_path = file_handler._get_file_path(file_id)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    try:
        mining_service = DataMiningService(file_path)
        columns_info = mining_service.get_columns_info()
        return columns_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@router.post("/analyze", response_model=MiningResponse)
async def analyze_data(
    request: MiningRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform data mining analysis"""
    # Verify file ownership
    db_file = db.query(DBFile).filter(
        DBFile.file_id == request.file_id,
        DBFile.user_id == current_user.id
    ).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get file path
    file_handler = FileHandler()
    file_path = file_handler._get_file_path(request.file_id)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    try:
        mining_service = DataMiningService(file_path)
        
        # Perform analysis based on type
        if request.analytics_type == "correlation":
            if len(request.columns) != 2:
                raise HTTPException(status_code=400, detail="Correlation requires exactly 2 columns")
            results = mining_service.correlation_analysis(request.columns[0], request.columns[1])
        
        elif request.analytics_type == "clustering":
            if len(request.columns) < 2:
                raise HTTPException(status_code=400, detail="Clustering requires at least 2 columns")
            n_clusters = request.parameters.get("n_clusters", 3)
            results = mining_service.clustering_analysis(request.columns, n_clusters)
        
        elif request.analytics_type == "classification":
            if len(request.columns) < 2:
                raise HTTPException(status_code=400, detail="Classification requires target + at least 1 feature")
            target = request.columns[0]
            features = request.columns[1:]
            test_size = request.parameters.get("test_size", 0.2)
            results = mining_service.classification_analysis(target, features, test_size)
        
        elif request.analytics_type == "regression":
            if len(request.columns) < 2:
                raise HTTPException(status_code=400, detail="Regression requires target + at least 1 feature")
            target = request.columns[0]
            features = request.columns[1:]
            test_size = request.parameters.get("test_size", 0.2)
            results = mining_service.regression_analysis(target, features, test_size)
        
        elif request.analytics_type == "association":
            if len(request.columns) < 2:
                raise HTTPException(status_code=400, detail="Association rules require at least 2 columns")
            min_support = request.parameters.get("min_support", 0.01)
            results = mining_service.association_rules_analysis(request.columns, min_support)
        
        elif request.analytics_type == "descriptive":
            if len(request.columns) < 1:
                raise HTTPException(status_code=400, detail="Descriptive stats require at least 1 column")
            results = mining_service.descriptive_statistics(request.columns)
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown analytics type: {request.analytics_type}")
        
        return MiningResponse(
            analytics_type=request.analytics_type,
            results=results,
            columns_used=request.columns
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
