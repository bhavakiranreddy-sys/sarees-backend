from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    description = Column(String(255))

    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(String(255))
    price = Column(Float)
    bulk_price = Column(Float) # Price for bulk orders
    min_bulk_quantity = Column(Integer, default=10)
    stock_quantity = Column(Integer)
    category_id = Column(Integer, ForeignKey("categories.id"))
    vendor_id = Column(Integer, ForeignKey("vendor_profiles.id"))
    
    # Saree Specific Fields
    fabric_type = Column(String(255))
    color = Column(String(255))
    occasion = Column(String(255))
    sku = Column(String(255), unique=True)
    images = Column(JSON) # List of image URLs
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    category = relationship("Category", back_populates="products")
    vendor = relationship("VendorProfile", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
