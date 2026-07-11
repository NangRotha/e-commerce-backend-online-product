from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, products, orders, admin, cart, upload, pages

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce API",
    description="Complete e-commerce platform API",
    version="1.0.0"
)

# ===== CORS Configuration (បានកែតម្រូវសម្រាប់ Production) =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",                          # Frontend-User (Dev)
        "http://localhost:5174",                          # Frontend-Admin (Dev)
        "https://e-commerce-user-online-product.vercel.app",  # Frontend-User (Vercel)
        "https://e-commerce-admin-online-product.vercel.app", # Frontend-Admin (Vercel)
        "https://e-commerce-backend-online-product.onrender.com", # Backend (Render)
    ],
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

@app.get("/")
def root():
    return {"message": "Welcome to E-Commerce API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}