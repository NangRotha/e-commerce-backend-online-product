import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base, SessionLocal
from .models import User
from .auth import get_password_hash

# ===== នាំចូល Routers ទាំងអស់ =====
from .routers import auth, products, cart, orders, admin, pages

app = FastAPI(title="E-Commerce API")

# Startup event to create admin user
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            print("Creating default admin user...")
            new_admin = User(
                username="admin",
                email="admin@marketplace.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                is_active=True,
                is_admin=True
            )
            db.add(new_admin)
            db.commit()
            print("Default admin user created successfully! (admin / admin123)")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Startup admin creation failed: {e}")
    finally:
        db.close()

# ==============================================================================
# CORS (Updated with your Vercel Domain)
# ==============================================================================
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://e-commerce-user-online-product.vercel.app",
    "https://e-commerce-admin-online-product.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# Static Files
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
if not os.path.exists(UPLOAD_DIR): 
    os.makedirs(UPLOAD_DIR)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ==============================================================================
# Database
# ==============================================================================
Base.metadata.create_all(bind=engine)

# ==============================================================================
# ✅ បញ្ជាក់ Routes ឲ្យច្បាស់ដោយឡែកពីគ្នា ដើម្បីកុំឲ្យមាន /api ពីរដង
# ==============================================================================

# 1. Auth Router: យើងកំណត់ prefix="/api" តែនៅទីនេះ
#    ធ្វើដូចនេះ ប្រសិនបើក្នុង auth.py មាន @router.post("/login") 
#    ផ្លូវពេញនឹងក្លាយជា /api/login (មិនមែន /api/api/auth/login ទេ)
app.include_router(auth.router, prefix="/api")       

# 2. Routers ផ្សេងទៀត: ពួកវាអាចនៅត្រង់ Root ឬប្រើ Prefix ផ្សេង។ 
#    សម្រាប់ភាពស៊ីសង្វាក់គ្នា យើងក៏បន្ថែម prefix="/api" ដូចគ្នា។
#    យកចិត្តទុកដាក់៖ នៅក្នុង routers/orders.py ជាដើម ត្រូវប្រាកដថា @router មានតែផ្លូវខ្លីៗ 
#    (ឧ. @router.get("/orders") មិនមែន @router.get("/api/orders") ទេ)។
app.include_router(products.router, prefix="/api")   
app.include_router(cart.router, prefix="/api")       
app.include_router(orders.router, prefix="/api")     
app.include_router(admin.router, prefix="/api")      
app.include_router(pages.router, prefix="/api")      

@app.get("/")
async def root():
    return {"message": "E-Commerce API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}