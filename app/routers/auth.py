from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app import schemas, crud, auth, models
from app.database import get_db
from app.config import settings
import os

# === ពិនិត្យ Google Libraries ===
try:
    from google.oauth2 import id_token
    from google.auth.transport import requests
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    return crud.create_user(db=db, user=user)

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: schemas.UserResponse = Depends(auth.get_current_active_user_dependency)):
    return current_user

@router.put("/me", response_model=schemas.UserResponse)
def update_profile(
    user_update: schemas.UserUpdate, 
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(auth.get_current_active_user_dependency)
):
    return crud.update_user(db=db, user_id=current_user.id, user_update=user_update)

@router.post("/create-admin")
def create_admin(
    username: str,
    password: str,
    email: str = "admin@example.com",
    full_name: str = "Admin User",
    db: Session = Depends(get_db)
):
    existing = crud.get_user_by_username(db, username=username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    existing_email = crud.get_user_by_email(db, email=email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already taken")
    hashed_password = auth.get_password_hash(password)
    admin = models.User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name=full_name,
        is_active=True,
        is_admin=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return {"message": f"Admin user '{username}' created successfully"}

# ===== Google Login Endpoint with safe import =====
@router.post("/google/callback", response_model=schemas.Token)
def google_login(token: str, db: Session = Depends(get_db)):
    """
    Google OAuth Login Callback
    ទទួល Token ពី Google និងបង្កើត JWT Token សម្រាប់អ្នកប្រើប្រាស់
    """
    if not GOOGLE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Google authentication is not configured properly. Missing google libraries.")
    
    try:
        CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        if not CLIENT_ID:
            raise HTTPException(status_code=500, detail="Google Client ID not configured")
        
        id_info = id_token.verify_oauth2_token(
            token, requests.Request(), CLIENT_ID
        )
        
        email = id_info.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        username = id_info.get('name', email.split('@')[0])
        full_name = id_info.get('name', '')
        picture = id_info.get('picture', None)
        
        user = db.query(models.User).filter(models.User.email == email).first()
        if not user:
            import secrets
            random_password = secrets.token_hex(16)
            hashed_password = auth.get_password_hash(random_password)
            
            user = models.User(
                email=email,
                username=username,
                hashed_password=hashed_password,
                full_name=full_name,
                profile_image_url=picture,
                is_active=True,
                is_admin=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google login failed: {str(e)}")