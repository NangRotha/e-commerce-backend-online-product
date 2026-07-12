from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, crud
from app.database import get_db
from app.auth import get_current_active_user_dependency

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("/", response_model=List[schemas.ProductResponse])
def read_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_new: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    products = crud.get_products(db, skip=skip, limit=limit, category=category, is_new=is_new)
    return products

# ===== បន្ថែម / នៅចុងបញ្ចប់ =====
@router.get("/featured/", response_model=List[schemas.ProductResponse])
def read_featured_products(limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_featured_products(db, limit=limit)

@router.get("/new/", response_model=List[schemas.ProductResponse])
def read_new_products(limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_new_products(db, limit=limit)

@router.get("/{product_id}", response_model=schemas.ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product