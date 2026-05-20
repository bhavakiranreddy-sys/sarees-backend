from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Delivery, Order, User, UserRole
from ..auth.deps import check_role

router = APIRouter(prefix="/delivery", tags=["Delivery Dashboard"])

@router.get("/my-deliveries")
def get_my_deliveries(
    current_user: User = Depends(check_role([UserRole.DELIVERY])),
    db: Session = Depends(get_db)
):
    if not current_user.delivery_profile:
        raise HTTPException(status_code=400, detail="Delivery profile not found")
    
    deliveries = db.query(Delivery).filter(Delivery.delivery_partner_id == current_user.delivery_profile.id).all()
    result = []
    for d in deliveries:
        order = db.query(Order).filter(Order.id == d.order_id).first()
        result.append({
            "id": d.id,
            "order_id": f"ORD-{order.id}" if order else f"ORD-UNK",
            "status": d.status,
            "total_amount": order.total_amount if order else 0,
            "buyer_name": order.buyer.business_name if order and order.buyer else "N/A",
            "destination": order.buyer.shipping_address if order and order.buyer else "N/A"
        })
    return result

@router.post("/update-status/{delivery_id}")
def update_delivery_status(
    delivery_id: int,
    status: str,
    current_user: User = Depends(check_role([UserRole.DELIVERY])),
    db: Session = Depends(get_db)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery record not found")
    
    delivery.status = status
    db.commit()
    return {"message": "Status updated successfully"}

@router.get("/available-deliveries", response_model=List[dict])
def get_available_deliveries(
    current_user: User = Depends(check_role([UserRole.DELIVERY])),
    db: Session = Depends(get_db)
):
    deliveries = db.query(Delivery).filter(Delivery.delivery_partner_id == None).all()
    result = []
    for d in deliveries:
        order = db.query(Order).filter(Order.id == d.order_id).first()
        result.append({
            "id": d.id,
            "order_id": f"ORD-{order.id}",
            "status": d.status,
            "total_amount": order.total_amount,
            "buyer_name": order.buyer.business_name if order.buyer else "N/A",
            "destination": order.buyer.shipping_address if order.buyer else "N/A"
        })
    return result

@router.post("/accept-delivery/{delivery_id}")
def accept_delivery(
    delivery_id: int,
    current_user: User = Depends(check_role([UserRole.DELIVERY])),
    db: Session = Depends(get_db)
):
    if not current_user.delivery_profile:
        raise HTTPException(status_code=400, detail="Delivery profile not found")
        
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery record not found")
    
    delivery.delivery_partner_id = current_user.delivery_profile.id
    delivery.status = "Picked up"
    db.commit()
    return {"message": "Delivery accepted successfully"}
