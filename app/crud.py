from sqlalchemy.orm import Session
from sqlalchemy import and_
from app import models, schemas
from app.auth import get_password_hash
import uuid
from datetime import datetime

# ===== User CRUD =====
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if db_user:
        update_data = user_update.dict(exclude_unset=True)
        if 'password' in update_data and update_data['password']:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        for key, value in update_data.items():
            if key != 'hashed_password':
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

# ===== Product CRUD =====
def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()

# ✅ មុខងារនេះត្រូវបានហៅដោយ @router.get("/products") នៅក្នុង admin.py
def get_products(db: Session, skip: int = 0, limit: int = 100, category: str = None, is_new: bool = None):
    query = db.query(models.Product)
    if category:
        query = query.filter(models.Product.category == category)
    if is_new is not None:
        query = query.filter(models.Product.is_new == is_new)
    return query.offset(skip).limit(limit).all()

def get_featured_products(db: Session, limit: int = 10):
    return db.query(models.Product).filter(models.Product.is_featured == True).limit(limit).all()

def get_new_products(db: Session, limit: int = 10):
    return db.query(models.Product).filter(models.Product.is_new == True).order_by(models.Product.created_at.desc()).limit(limit).all()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, product_id: int, product_update: schemas.ProductUpdate):
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product

# ===== Order CRUD =====
def create_order(db: Session, order: schemas.OrderCreate, user_id: int):
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    db_order = models.Order(
        order_number=order_number,
        user_id=user_id,
        total_amount=0,
        shipping_address=order.shipping_address,
        payment_method=order.payment_method,
        coupon_code=order.coupon_code,
        customer_name="Guest",
        payment_status=order.payment_status
    )
    db.add(db_order)
    db.flush()
    
    total_amount = 0
    discount_percent = order.discount_percent or 0.0

    for item in order.items:
        product = get_product(db, item.product_id)
        if product:
            unit_price = product.discounted_price or product.price
            total_price = unit_price * item.quantity
            total_amount += total_price
            db_order_item = models.OrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=unit_price,
                total_price=total_price
            )
            db.add(db_order_item)
            product.stock_quantity -= item.quantity
    
    if discount_percent > 0:
        total_amount = total_amount * (1 - discount_percent)
    
    db_order.total_amount = total_amount
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, user_id: int = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Order)
    if user_id:
        query = query.filter(models.Order.user_id == user_id)
    return query.order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

# ===== Cart CRUD =====
def get_cart_items(db: Session, user_id: int):
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()

def add_to_cart(db: Session, cart_item: schemas.CartItemBase, user_id: int):
    existing_item = db.query(models.CartItem).filter(
        and_(models.CartItem.user_id == user_id, 
             models.CartItem.product_id == cart_item.product_id)
    ).first()
    if existing_item:
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        db_cart_item = models.CartItem(
            user_id=user_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(db_cart_item)
        db.commit()
        db.refresh(db_cart_item)
        return db_cart_item

def remove_from_cart(db: Session, cart_item_id: int, user_id: int):
    db_cart_item = db.query(models.CartItem).filter(
        and_(models.CartItem.id == cart_item_id, models.CartItem.user_id == user_id)
    ).first()
    if db_cart_item:
        db.delete(db_cart_item)
        db.commit()
    return db_cart_item

# ===== Settings CRUD =====
def get_settings(db: Session):
    setting = db.query(models.Setting).first()
    if not setting:
        setting = models.Setting()
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting

def update_settings(db: Session, settings_update: schemas.SettingsUpdate):
    setting = get_settings(db)
    update_data = settings_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(setting, key, value)
    db.commit()
    db.refresh(setting)
    return setting

# ===== Page CRUD =====
def get_page(db: Session, slug: str):
    return db.query(models.Page).filter(models.Page.slug == slug).first()

def get_pages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Page).offset(skip).limit(limit).all()

def create_page(db: Session, page: schemas.PageCreate):
    db_page = models.Page(**page.dict())
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

def update_page(db: Session, slug: str, page_update: schemas.PageUpdate):
    db_page = get_page(db, slug)
    if db_page:
        update_data = page_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_page, key, value)
        db.commit()
        db.refresh(db_page)
    return db_page

def delete_page(db: Session, slug: str):
    db_page = get_page(db, slug)
    if db_page:
        db.delete(db_page)
        db.commit()
    return db_page