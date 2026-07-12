from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud, models
from app.database import get_db
from app.auth import get_current_active_user_dependency

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.post("/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db),
                 current_user: schemas.UserResponse = Depends(get_current_active_user_dependency)):
    order_dict = order.dict()
    order_dict['customer_name'] = "Guest"
    db_order = crud.create_order(db=db, order=schemas.OrderCreate(**order_dict), user_id=current_user.id)
    
    if current_user and current_user.full_name:
        db_order.customer_name = current_user.full_name
        db.commit()
        db.refresh(db_order)
    
    return db_order

@router.get("/", response_model=List[schemas.OrderResponse])
def get_user_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                    current_user: schemas.UserResponse = Depends(get_current_active_user_dependency)):
    orders = crud.get_orders(db, user_id=current_user.id, skip=skip, limit=limit)
    for order in orders:
        order_items = db.query(models.OrderItem).filter(models.OrderItem.order_id == order.id).all()
        order.items = [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total_price": item.total_price,
                "product_name": db.query(models.Product).filter(models.Product.id == item.product_id).first().name
            }
            for item in order_items
        ]
    return orders

@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db),
              current_user: schemas.UserResponse = Depends(get_current_active_user_dependency)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order or (order.user_id != current_user.id and not current_user.is_admin):
        raise HTTPException(status_code=404, detail="Order not found")
    return order