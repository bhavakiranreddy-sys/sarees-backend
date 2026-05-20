from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Order, OrderItem, Product, User, UserRole, OrderStatus, Delivery
from ..schemas import OrderCreate, OrderResponse
from ..auth.deps import get_current_user, check_role

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderResponse)
def create_order(
    order_in: OrderCreate,
    current_user: User = Depends(check_role([UserRole.BUYER, UserRole.ADMIN_SELLER])),
    db: Session = Depends(get_db)
):
    if not current_user.buyer_profile:
        # Auto-create buyer profile for admin/seller if missing
        from ..models import BuyerProfile
        new_profile = BuyerProfile(user_id=current_user.id, business_name=current_user.full_name)
        db.add(new_profile)
        db.commit()
        db.refresh(current_user)
    
    if order_in.shipping_address:
        current_user.buyer_profile.shipping_address = order_in.shipping_address
        db.commit()

    buyer_id = current_user.buyer_profile.id
    total_amount = 0
    items_to_create = []
    
    for item in order_in.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        # Use bulk price if quantity meets minimum
        price = product.bulk_price if item.quantity >= product.min_bulk_quantity else product.price
        total_amount += price * item.quantity
        
        items_to_create.append(OrderItem(
            product_id=product.id,
            quantity=item.quantity,
            price_at_purchase=price
        ))
        
        # Deduct stock
        if product.stock_quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product.name}")
        product.stock_quantity -= item.quantity

    new_order = Order(
        buyer_id=buyer_id,
        total_amount=total_amount,
        status=OrderStatus.PENDING
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    for item in items_to_create:
        item.order_id = new_order.id
        db.add(item)
    
    db.commit()
    db.refresh(new_order)
    # Create delivery record
    new_delivery = Delivery(
        order_id=new_order.id,
        status="pending"
    )
    db.add(new_delivery)
    db.commit()

    return new_order

@router.get("/my-orders", response_model=List[OrderResponse])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == UserRole.BUYER:
        return db.query(Order).filter(Order.buyer_id == current_user.buyer_profile.id).all()
    elif current_user.role == UserRole.ADMIN_SELLER:
        # Orders containing vendor's products
        return db.query(Order).join(OrderItem).join(Product).filter(Product.vendor_id == current_user.vendor_profile.id).distinct().all()
    return []
