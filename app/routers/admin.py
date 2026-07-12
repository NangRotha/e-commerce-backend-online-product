from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app import schemas, crud, models
from app.database import get_db
from app.auth import get_current_admin_user_dependency
from app.utils.cloudinary_upload import upload_image, delete_image

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/products", response_model=List[schemas.ProductResponse])
def get_all_products(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)
):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products

@router.post("/products", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db), 
                   admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)):
    return crud.create_product(db=db, product=product)

@router.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product_update: schemas.ProductUpdate, 
                   db: Session = Depends(get_db), 
                   admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)):
    product = crud.update_product(db, product_id, product_update)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), 
                   admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)):
    product = crud.delete_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@router.get("/settings", response_model=schemas.SettingsResponse)
def get_settings(db: Session = Depends(get_db), 
                 admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)):
    return crud.get_settings(db)

@router.put("/settings", response_model=schemas.SettingsResponse)
def update_settings(settings_update: schemas.SettingsUpdate, 
                    db: Session = Depends(get_db), 
                    admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)):
    return crud.update_settings(db, settings_update)

@router.get("/settings/public", response_model=schemas.SettingsResponse)
def get_public_settings(db: Session = Depends(get_db)):
    return crud.get_settings(db)

@router.post("/upload")
def upload_image_endpoint(file: UploadFile = File(...)):
    try:
        result = upload_image(file)
        return {"url": result["secure_url"], "public_id": result["public_id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/orders", response_model=List[schemas.OrderResponse])
def get_all_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                   admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)):
    orders = crud.get_orders(db, skip=skip, limit=limit)
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

@router.put("/orders/{order_id}/status")
def update_order_status(order_id: int, status: str, payment_status: Optional[str] = None, db: Session = Depends(get_db),
                        admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    if payment_status:
        order.payment_status = payment_status
    db.commit()
    return {"message": "Order status updated successfully"}

@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db),
                         admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)):
    total_products = db.query(models.Product).count()
    total_orders = db.query(models.Order).count()
    total_revenue = db.query(func.sum(models.Order.total_amount)).scalar() or 0.0
    total_users = db.query(models.User).filter(models.User.is_admin == False).count()
    recent_orders = db.query(models.Order).order_by(models.Order.created_at.desc()).limit(5).all()
    for order in recent_orders:
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
    return {
        "totalProducts": total_products,
        "totalOrders": total_orders,
        "totalRevenue": total_revenue,
        "totalUsers": total_users,
        "recentOrders": recent_orders
    }

@router.get("/dashboard/chart-data")
def get_chart_data(db: Session = Depends(get_db),
                    admin: schemas.UserResponse = Depends(get_current_admin_user_dependency)):
    from datetime import datetime, timedelta
    import random
    
    data = []
    today = datetime.now()
    for i in range(7):
        day = today - timedelta(days=i)
        data.append({
            "name": day.strftime("%b %d"),
            "orders": random.randint(5, 20),
            "revenue": random.randint(100, 500)
        })
    data.reverse()
    return data