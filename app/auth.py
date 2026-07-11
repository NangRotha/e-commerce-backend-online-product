from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app import models, schemas
from app.config import settings
from app.database import get_db

# ការកំណត់ Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password, hashed_password):
    """ពិនិត្យពាក្យសម្ងាត់ត្រឹមត្រូវឬអត់"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """ធ្វើ encryption ពាក្យសម្ងាត់"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(
        (models.User.username == username) | (models.User.email == username)
    ).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """បង្កើត JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """ទាញយកអ្នកប្រើប្រាស់បច្ចុប្បន្នពី token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    """ពិនិត្យអ្នកប្រើប្រាស់សកម្ម"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_admin_user(current_user: models.User = Depends(get_current_active_user)):
    """ពិនិត្យអ្នកប្រើប្រាស់ជា Admin"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# ===========================================
# មុខងារ Dependency ដែលខ្វះ (បន្ថែមនេះដើម្បីដោះស្រាយបញ្ហា)
# ===========================================

def get_current_user_dependency(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependency សម្រាប់ទាញយកអ្នកប្រើប្រាស់បច្ចុប្បន្ន"""
    return get_current_user(token, db)

def get_current_active_user_dependency(current_user: models.User = Depends(get_current_user_dependency)):
    """Dependency សម្រាប់ទាញយកអ្នកប្រើប្រាស់សកម្ម"""
    return get_current_active_user(current_user)

def get_current_admin_user_dependency(current_user: models.User = Depends(get_current_active_user_dependency)):
    """Dependency សម្រាប់ទាញយកអ្នកប្រើប្រាស់ Admin"""
    return get_current_admin_user(current_user)