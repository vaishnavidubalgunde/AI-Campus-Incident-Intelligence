from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db
from backend.app.models.entities import Department, IncidentCategory
from backend.app.schemas.schemas import DepartmentResponse, CategoryResponse

router = APIRouter()

@router.get("/departments", response_model=List[DepartmentResponse])
def get_departments(db: Session = Depends(get_db)):
    return db.query(Department).filter(Department.is_active == True).order_by(Department.name).all()

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(IncidentCategory).order_by(IncidentCategory.name).all()
