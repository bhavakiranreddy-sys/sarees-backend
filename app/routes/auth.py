from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, VendorProfile, BuyerProfile, DeliveryProfile, UserRole
from ..schemas import UserCreate, UserResponse, Token
from ..auth.hash import get_password_hash, verify_password
from ..auth.jwt_handler import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_pw,
        full_name=user_in.full_name,
        role=user_in.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create profile based on role
    if new_user.role == UserRole.ADMIN_SELLER:
        profile = VendorProfile(user_id=new_user.id)
        db.add(profile)
    elif new_user.role == UserRole.BUYER:
        profile = BuyerProfile(user_id=new_user.id)
        db.add(profile)
    elif new_user.role == UserRole.DELIVERY:
        profile = DeliveryProfile(user_id=new_user.id)
        db.add(profile)
    
    db.commit()
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role.value
    }
