from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db
from app.auth import get_current_active_user_dependency

router = APIRouter(prefix="/api/cart", tags=["Cart"])

# ត្រូវប្រាកដថាមាន / នៅខាងចុងបញ្ចប់
@router.get("/", response_model=List[schemas.CartItemResponse])
def get_cart(db: Session = Depends(get_db),
             current_user: schemas.UserResponse = Depends(get_current_active_user_dependency)):
    return crud.get_cart_items(db, current_user.id)

@router.post("/", response_model=schemas.CartItemResponse)
def add_to_cart(cart_item: schemas.CartItemBase, db: Session = Depends(get_db),
                current_user: schemas.UserResponse = Depends(get_current_active_user_dependency)):
    return crud.add_to_cart(db, cart_item, current_user.id)

@router.delete("/{cart_item_id}")
def remove_from_cart(cart_item_id: int, db: Session = Depends(get_db),
                     current_user: schemas.UserResponse = Depends(get_current_active_user_dependency)):
    item = crud.remove_from_cart(db, cart_item_id, current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return {"message": "Item removed from cart"}