from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, crud, auth

def seed_admin():
    db: Session = SessionLocal()
    try:
        existing = db.query(models.User).filter(models.User.username == "admin").first()
        if existing:
            print("Admin user already exists.")
            return

        hashed_password = auth.get_password_hash("admin123")
        admin = models.User(
            email="admin@example.com",
            username="admin",
            hashed_password=hashed_password,
            full_name="Admin User",
            is_active=True,
            is_admin=True,
        )
        db.add(admin)
        db.commit()
        print("Admin user created: username=admin, password=admin123")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
