from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from ..database import Base

class UserRole(str, enum.Enum):
    ADMIN_SELLER = "admin_seller"
    BUYER = "buyer"
    DELIVERY = "delivery"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.BUYER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Profiles
    vendor_profile = relationship("VendorProfile", back_populates="user", uselist=False)
    buyer_profile = relationship("BuyerProfile", back_populates="user", uselist=False)
    delivery_profile = relationship("DeliveryProfile", back_populates="user", uselist=False)

class VendorProfile(Base):
    __tablename__ = "vendor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    business_name = Column(String(255))
    gst_number = Column(String(255))
    business_address = Column(String(255))
    shop_document_url = Column(String(255))
    is_approved = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="vendor_profile")
    products = relationship("Product", back_populates="vendor")

class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    business_name = Column(String(255))
    gst_number = Column(String(255))
    shipping_address = Column(String(255))
    
    user = relationship("User", back_populates="buyer_profile")
    orders = relationship("Order", back_populates="buyer")

class DeliveryProfile(Base):
    __tablename__ = "delivery_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vehicle_number = Column(String(255))
    current_location = Column(String(255))
    
    user = relationship("User", back_populates="delivery_profile")
    deliveries = relationship("Delivery", back_populates="delivery_partner")
