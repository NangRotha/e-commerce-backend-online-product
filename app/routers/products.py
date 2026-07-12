from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, crud
from app.database import get_db
from app.auth import get_current_active_user_dependency

router = APIRouter(prefix="/api/products", tags=["Products"])

# ============================================================
# 1. GET /api/products/    (Root - ទាញយកផលិតផលទាំងអស់)
# ============================================================
@router.get("/", response_model=List[schemas.ProductResponse])
def read_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_new: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    ទាញយកបញ្ជីផលិតផលទាំងអស់។
    អាចត្រងតាម category ឬ is_new។
    """
    products = crud.get_products(db, skip=skip, limit=limit, category=category, is_new=is_new)
    return products

# ============================================================
# 2. GET /api/products/featured/    (ផលិតផលពិសេស)
# ============================================================
@router.get("/featured/", response_model=List[schemas.ProductResponse])
def read_featured_products(limit: int = 10, db: Session = Depends(get_db)):
    """
    ទាញយកបញ្ជីផលិតផលពិសេស (is_featured=True)។
    """
    return crud.get_featured_products(db, limit=limit)

# ============================================================
# 3. GET /api/products/new/    (ផលិតផលថ្មីៗ)
# ============================================================
@router.get("/new/", response_model=List[schemas.ProductResponse])
def read_new_products(limit: int = 10, db: Session = Depends(get_db)):
    """
    ទាញយកបញ្ជីផលិតផលថ្មីៗ (is_new=True) តម្រៀបតាមកាលបរិច្ឆេទថ្មីបំផុត។
    """
    return crud.get_new_products(db, limit=limit)

# ============================================================
# 4. GET /api/products/{product_id}    (ផលិតផលនីមួយៗ)
# ============================================================
@router.get("/{product_id}", response_model=schemas.ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    ទាញយកព័ត៌មានលម្អិតនៃផលិតផលនីមួយៗដោយផ្អែកលើ ID។
    """
    product = crud.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product