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
# ✅ FIX 1: CORS (ត្រូវប្រាកដថាបន្ថែម Domain Vercel និង Localhost)
# ==============================================================================
# ដើម្បីសុវត្ថិភាព គួរតែកំណត់ List ច្បាស់លាស់ មិនមែនប្រើ Env Variable ទទេនោះទេ
# ប៉ុន្តែប្រសិនបើលោកអ្នកចង់ប្រើ Env Variable ត្រូវប្រាកដថានៅក្នុង Render Dashboard មានកំណត់ ALLOWED_ORIGINS នេះ
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://e-commerce-user-online-product.vercel.app",
    "https://e-commerce-admin-online-product.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, # ✅ ប្រើ List ត្រឹមត្រូវ
    allow_credentials=True,       # ✅ អនុញ្ញាតឲ្យផ្ញើ Cookie / Token
    allow_methods=["*"],          # ✅ អនុញ្ញាតគ្រប់ Method (GET, POST, PUT, DELETE)
    allow_headers=["*"],          # ✅ អនុញ្ញាតគ្រប់ Headers
)

# ==============================================================================
# Static Files (មិនបាច់កែ)
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
# ✅ FIX 2: Routers (បន្ថែម Prefix តែម្ដងធ្វើឲ្យ Frontend ងាយស្រួលហៅ)
# ==============================================================================
# ក្នុង Frontend api.js របស់លោកអ្នក បានកំណត់ baseURL ទៅ .../api ហើយ
# ដូច្នេះលោកអ្នកត្រូវបន្ថែម prefix="/api" នៅទីនេះដើម្បីឲ្យវាត្រូវគ្នា។

app.include_router(auth.router, prefix="/api")       # ✅ បន្ថែម prefix
app.include_router(products.router, prefix="/api")   # ✅ បន្ថែម prefix
app.include_router(cart.router, prefix="/api")       # ✅ បន្ថែម prefix
app.include_router(orders.router, prefix="/api")     # ✅ បន្ថែម prefix
app.include_router(admin.router, prefix="/api")      # ✅ បន្ថែម prefix
app.include_router(pages.router, prefix="/api")      # ✅ បន្ថែម prefix

@app.get("/")
async def root():
    return {"message": "E-Commerce API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}