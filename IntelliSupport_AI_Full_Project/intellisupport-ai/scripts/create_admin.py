from app.database import SessionLocal
from app.models import User
from app.security import hash_password
print("Create an admin account. Run only in a trusted terminal.")
email=input("Admin email: ").strip().lower()
name=input("Admin name: ").strip()
password=input("Admin password (min 12 chars): ")
if len(password)<12: raise SystemExit("Password too short")
with SessionLocal() as db:
    if db.query(User).filter_by(email=email).first(): raise SystemExit("User already exists")
    db.add(User(email=email,name=name,password_hash=hash_password(password),role="admin"))
    db.commit()
print("Admin created.")
