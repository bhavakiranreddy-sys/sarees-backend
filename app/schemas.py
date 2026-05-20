from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from .models.user import UserRole

# Auth Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.BUYER

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
class VendorProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    gst_number: Optional[str] = None
    business_address: Optional[str] = None
    shop_document_url: Optional[str] = None

class VendorProfileResponse(VendorProfileUpdate):
    id: int
    user_id: int
    is_approved: bool

    class Config:
        from_attributes = True
# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    bulk_price: float
    min_bulk_quantity: int = 10
    stock_quantity: int
    category_id: int
    fabric_type: str
    color: str
    occasion: str
    sku: str
    images: List[str] = []

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    vendor_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Order Schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemBase]
    shipping_address: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
