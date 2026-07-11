from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, get_current_active_user, get_current_admin_user
from app import models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user_dependency(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        user = get_current_user(token, db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_active_user_dependency(current_user: models.User = Depends(get_current_user_dependency)):
    try:
        return get_current_active_user(current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_current_admin_user_dependency(current_user: models.User = Depends(get_current_active_user_dependency)):
    try:
        return get_current_admin_user(current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))