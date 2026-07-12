from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, products, orders, admin, cart, upload, pages
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce API",
    description="Complete e-commerce platform API",
    version="1.0.0"
)

# ==============================================================================
# ទាញយក Allowed Origins ពី Environment Variables
# ==============================================================================
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "")
if ALLOWED_ORIGINS_STR:
    ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",") if origin.strip()]
else:
    ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://e-commerce-user-online-product.vercel.app",
        "https://e-commerce-admin-online-product.vercel.app",
        "https://e-commerce-backend-online-product.onrender.com",
    ]

print(f"Allowed Origins: {ALLOWED_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(cart.router)
app.include_router(upload.router)
app.include_router(pages.router)

# ==============================================================================
# បង្កើត Admin User ដោយស្វ័យប្រវត្តិនៅពេល Start
# ==============================================================================
@app.on_event("startup")
def startup_event():
    from sqlalchemy.orm import Session
    from app.database import SessionLocal
    from app import models
    from app.auth import get_password_hash

    db: Session = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.username == "admin").first()
        if not existing:
            print("Creating default admin user...")
            admin = models.User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                is_active=True,
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            print("Default admin user created successfully! (admin / admin123)")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Startup admin creation failed: {e}")
    finally:
        db.close()

# ==============================================================================
# Root Endpoint
# ==============================================================================
@app.get("/")
def root():
    return {"message": "Welcome to E-Commerce API"}

# ==============================================================================
# Health Check Endpoint
# ==============================================================================
@app.get("/health")
def health_check():
    return {"status": "healthy"}
