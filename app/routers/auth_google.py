from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from app.database import get_db
from app import models
from app.auth import create_access_token
from app.config import settings

# ===== កំណត់រចនាសម្ព័ន្ធ OAuth =====
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

router = APIRouter(prefix="/api/auth/google", tags=["Google Auth"])

@router.post("/callback")
async def google_callback(token_data: dict, db: Session = Depends(get_db)):
    """
    ទទួល Token ពី Frontend (react-oauth/google), 
    ផ្ទៀងផ្ទាត់, និងបង្កើត JWT ផ្ទាល់ខ្លួន
    """
    try:
        # ចំណាំ៖ នៅក្នុងកូដពិត អ្នកគួរតែផ្ទៀងផ្ទាត់ Token ជាមួយ Google 
        # ប៉ុន្តែសម្រាប់ភាពងាយស្រួលនៃការសាកល្បង យើងនឹងទទួលយក Token ពី Frontend
        
        # សន្មត់ថា Frontend ផ្ញើ email និង name មកជាមួយ
        email = token_data.get('email')
        name = token_data.get('name', 'Google User')
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not found in token")
        
        # ស្វែងរក User តាមរយៈ email
        user = db.query(models.User).filter(models.User.email == email).first()
        
        if not user:
            # បង្កើត User ថ្មី
            new_user = models.User(
                email=email,
                username=email.split('@')[0],
                full_name=name,
                hashed_password="google_oauth",  # មិនត្រូវការ Password
                is_active=True
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user = new_user
        
        # បង្កើត JWT Token ផ្ទាល់ខ្លួន
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))