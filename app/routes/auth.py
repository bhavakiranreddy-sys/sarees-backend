import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..database import get_db
from ..models import User, VendorProfile, BuyerProfile, DeliveryProfile, UserRole
from ..schemas import UserCreate, UserResponse, Token
from ..auth.hash import get_password_hash, verify_password
from ..auth.jwt_handler import create_access_token, create_refresh_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Signup attempt for email: {user_in.email} | role: {user_in.role}")

    # Check for duplicate email
    try:
        db_user = db.query(User).filter(User.email == user_in.email).first()
    except SQLAlchemyError as exc:
        logger.error(f"Database error while checking for existing user ({user_in.email}): {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable. Please try again later.",
        )

    if db_user:
        logger.warning(f"Signup rejected — email already registered: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email address already exists.",
        )

    # Hash password and persist the new user
    try:
        hashed_pw = get_password_hash(user_in.password)
        new_user = User(
            email=user_in.email,
            hashed_password=hashed_pw,
            full_name=user_in.full_name,
            role=user_in.role,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User created successfully: id={new_user.id} email={new_user.email}")
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Database error while creating user ({user_in.email}): {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not create account due to a database error. Please try again.",
        )

    # Create role-specific profile
    try:
        if new_user.role == UserRole.ADMIN_SELLER:
            db.add(VendorProfile(user_id=new_user.id))
            logger.info(f"VendorProfile created for user id={new_user.id}")
        elif new_user.role == UserRole.BUYER:
            db.add(BuyerProfile(user_id=new_user.id))
            logger.info(f"BuyerProfile created for user id={new_user.id}")
        elif new_user.role == UserRole.DELIVERY:
            db.add(DeliveryProfile(user_id=new_user.id))
            logger.info(f"DeliveryProfile created for user id={new_user.id}")
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(f"Database error while creating profile for user id={new_user.id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Account created but profile setup failed. Please contact support.",
        )

    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    logger.info(f"Login attempt for email: {form_data.username}")

    # Fetch user from database
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
    except SQLAlchemyError as exc:
        logger.error(f"Database error during login for ({form_data.username}): {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable. Please try again later.",
        )

    if not user:
        logger.warning(f"Login failed — no account found for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No account found with that email address.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed — incorrect password for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please try again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning(f"Login failed — account is inactive: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated. Please contact support.",
        )

    access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
    refresh_token = create_refresh_token(data={"sub": user.email})
    logger.info(f"Login successful for email: {user.email} | role: {user.role.value}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role.value,
    }
