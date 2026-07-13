from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# ===== User Schemas =====
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    profile_image_url: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ===== Product Schemas =====
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    discounted_price: Optional[float] = None
    category: str
    subcategory: Optional[str] = None
    stock_quantity: int = 0
    is_new: bool = True
    is_featured: bool = False
    specifications: Optional[Dict[str, Any]] = None

class ProductCreate(ProductBase):
    image_url: str
    image_public_id: Optional[str] = None
    sub_images: List[str] = []

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    discounted_price: Optional[float] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    stock_quantity: Optional[int] = None
    is_new: Optional[bool] = None
    is_featured: Optional[bool] = None
    image_url: Optional[str] = None
    sub_images: Optional[List[str]] = None
    specifications: Optional[Dict[str, Any]] = None

class ProductResponse(ProductBase):
    id: int
    image_url: str
    sub_images: List[str] = []
    rating: Optional[float] = 0.0
    reviews_count: Optional[int] = 0
    created_at: datetime
    
    class Config:
        orm_mode = True

# ===== Order Schemas =====
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    shipping_address: Dict[str, Any]
    payment_method: str
    items: List[OrderItemBase]
    coupon_code: Optional[str] = None
    discount_percent: Optional[float] = 0.0  # <--- បន្ថែមនេះ
    payment_status: Optional[str] = "pending"

class OrderResponse(BaseModel):
    id: int
    order_number: str
    total_amount: float
    status: str
    customer_name: Optional[str] = None
    payment_status: str
    created_at: datetime
    items: Optional[List[Dict[str, Any]]] = []
    
    class Config:
        orm_mode = True

# ===== Cart Schemas =====
class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product: ProductResponse
    quantity: int
    
    class Config:
        orm_mode = True

# ===== Settings Schemas =====
class SettingsUpdate(BaseModel):
    site_name: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    slide_images: Optional[List[str]] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    promo_title: Optional[str] = None
    promo_subtitle: Optional[str] = None
    promo_button_text: Optional[str] = None
    promo_code: Optional[str] = None
    promo_is_active: Optional[bool] = None

class SettingsResponse(BaseModel):
    site_name: str
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    slide_images: List[str] = []
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    promo_title: str
    promo_subtitle: str
    promo_button_text: str
    promo_code: str
    promo_is_active: bool
    
    class Config:
        orm_mode = True

# ===== Page Schemas =====
class PageBase(BaseModel):
    slug: str
    title: str
    content: str
    image_url: Optional[str] = None
    features: List[str] = []
    gallery_images: List[str] = []
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    is_published: bool = True

class PageCreate(PageBase):
    pass

class PageUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    features: Optional[List[str]] = None
    gallery_images: Optional[List[str]] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    is_published: Optional[bool] = None

class PageResponse(PageBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True