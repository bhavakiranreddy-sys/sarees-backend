from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Product, Category, User, UserRole
from ..schemas import ProductCreate, ProductResponse
from ..auth.deps import get_current_user, check_role

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[ProductResponse])
def get_products(
    category_id: Optional[int] = None,
    fabric: Optional[str] = None,
    color: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if fabric:
        query = query.filter(Product.fabric_type == fabric)
    if color:
        query = query.filter(Product.color == color)
    return query.all()

@router.post("/", response_model=ProductResponse)
def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(check_role([UserRole.ADMIN_SELLER])),
    db: Session = Depends(get_db)
):
    # Ensure vendor profile exists
    if not current_user.vendor_profile:
        raise HTTPException(status_code=400, detail="Vendor profile not found")
    
    new_product = Product(
        **product_in.model_dump(),
        vendor_id=current_user.vendor_profile.id
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
