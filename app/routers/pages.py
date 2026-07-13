# app/routers/pages.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud, models
from app.database import get_db
from app.auth import get_current_admin_user_dependency

router = APIRouter(prefix="/api/pages", tags=["Pages"])

@router.post("/", response_model=schemas.PageResponse)
def create_page(page: schemas.PageCreate, db: Session = Depends(get_db),
                admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)):
    existing = crud.get_page(db, slug=page.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Page with this slug already exists")
    return crud.create_page(db=db, page=page)

@router.get("/", response_model=List[schemas.PageResponse])
def read_pages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_pages(db, skip=skip, limit=limit)

@router.get("/{slug}", response_model=schemas.PageResponse)
def read_page(slug: str, db: Session = Depends(get_db)):
    page = crud.get_page(db, slug=slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@router.put("/{slug}", response_model=schemas.PageResponse)
def update_page(slug: str, page_update: schemas.PageUpdate, db: Session = Depends(get_db),
                admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)):
    page = crud.update_page(db, slug=slug, page_update=page_update)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@router.delete("/{slug}")
def delete_page(slug: str, db: Session = Depends(get_db),
                admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)):
    page = crud.delete_page(db, slug=slug)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"message": "Page deleted successfully"}