from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from ..models import User, BuyerProfile, Order, UserRole
from ..auth.deps import check_role

router = APIRouter(prefix="/buyer", tags=["Buyer Dashboard"])

@router.get("/stats")
def get_buyer_stats(
    current_user: User = Depends(check_role([UserRole.BUYER])),
    db: Session = Depends(get_db)
):
    if not current_user.buyer_profile:
        # Create profile if not exists (should have been created at signup)
        new_profile = BuyerProfile(user_id=current_user.id)
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        profile_id = new_profile.id
    else:
        profile_id = current_user.buyer_profile.id

    total_orders = db.query(Order).filter(Order.buyer_id == profile_id).count()
    total_spent = db.query(func.sum(Order.total_amount)).filter(Order.buyer_id == profile_id).scalar() or 0
    
    return {
        "total_orders": total_orders,
        "total_spent": total_spent,
        "wishlist_count": 0,  # Placeholder for now
        "loyalty_points": 150  # Demo value
    }

@router.get("/profile")
def get_buyer_profile(
    current_user: User = Depends(check_role([UserRole.BUYER])),
    db: Session = Depends(get_db)
):
    if not current_user.buyer_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return current_user.buyer_profile
