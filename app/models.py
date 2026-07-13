from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    profile_image_url = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    orders = relationship("Order", back_populates="user")
    cart_items = relationship("CartItem", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Float)
    discounted_price = Column(Float, nullable=True)
    category = Column(String)
    subcategory = Column(String, nullable=True)
    image_url = Column(String)
    image_public_id = Column(String, nullable=True)
    sub_images = Column(JSON, default=[])
    stock_quantity = Column(Integer, default=0)
    is_new = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    specifications = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    order_items = relationship("OrderItem", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_number = Column(String, unique=True, index=True)
    total_amount = Column(Float)
    coupon_code = Column(String, nullable=True)
    customer_name = Column(String, nullable=True)
    status = Column(String, default="pending")
    shipping_address = Column(JSON)
    payment_method = Column(String)
    payment_status = Column(String, default="pending")  # <--- បន្ថែមនេះ
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_price = Column(Float)
    
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

# ===== Page Model (For CMS Pages) =====
class Page(Base):
    __tablename__ = "pages"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True)
    title = Column(String)
    content = Column(Text)
    image_url = Column(String, nullable=True)
    features = Column(JSON, default=[])
    gallery_images = Column(JSON, default=[])
    meta_description = Column(String, nullable=True)
    meta_keywords = Column(String, nullable=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String, default="TechStore")
    logo_url = Column(String, nullable=True)
    logo_public_id = Column(String, nullable=True)
    favicon_url = Column(String, nullable=True)
    slide_images = Column(JSON, default=[])
    meta_description = Column(String, nullable=True)
    meta_keywords = Column(String, nullable=True)
    promo_title = Column(String, default="Special Offer: Get 20% Off Your First Order!")
    promo_subtitle = Column(String, default="Use code WELCOME20 at checkout")
    promo_button_text = Column(String, default="Shop Now")
    promo_code = Column(String, default="WELCOME20")
    promo_is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())