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

# ===== កែតម្រូវ CORS ឱ្យទទួលស្គាល់ Port 5175 =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Frontend-User
        "http://localhost:5174",  # Frontend-Admin (ធម្មតា)
        "http://localhost:5175",  # Frontend-Admin (បន្ថែមនេះ!)
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",  # បន្ថែម 127.0.0.1:5175 ផងដែរ
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