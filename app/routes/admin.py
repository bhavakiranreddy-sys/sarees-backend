from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..models import User, VendorProfile, Order, Product, UserRole
from ..auth.deps import check_role

router = APIRouter(prefix="/vendor", tags=["Vendor Dashboard"])

@router.get("/stats")
def get_vendor_stats(
    current_user: User = Depends(check_role([UserRole.VENDOR])),
    db: Session = Depends(get_db)
):
    total_sales = db.query(func.sum(Order.total_amount)).scalar() or 0
    total_orders = db.query(Order).count()
    pending_approvals = db.query(VendorProfile).filter(VendorProfile.is_approved == False).count()
    total_vendors = db.query(VendorProfile).count()
    total_buyers = db.query(User).filter(User.role == UserRole.BUYER).count()
    
    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "pending_approvals": pending_approvals,
        "total_vendors": total_vendors,
        "total_buyers": total_buyers
    }

@router.get("/pending-vendors", response_model=List[dict])
def get_pending_vendors(
    current_user: User = Depends(check_role([UserRole.VENDOR])),
    db: Session = Depends(get_db)
):
    vendors = db.query(VendorProfile).filter(VendorProfile.is_approved == False).all()
    return [{"id": v.id, "business_name": v.business_name, "gst": v.gst_number, "email": v.user.email} for v in vendors]

@router.post("/approve-vendor/{vendor_id}")
def approve_vendor(
    vendor_id: int,
    current_user: User = Depends(check_role([UserRole.VENDOR])),
    db: Session = Depends(get_db)
):
    vendor = db.query(VendorProfile).filter(VendorProfile.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    vendor.is_approved = True
    db.commit()
    return {"message": "Vendor approved successfully"}
