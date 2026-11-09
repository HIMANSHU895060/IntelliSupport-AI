import bcrypt, jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User
ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
def verify_password(password: str, hashed: str) -> bool:
    try: return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception: return False
def create_token(user: User) -> str:
    payload = {"sub": str(user.id), "email": user.email, "role": user.role,
               "exp": datetime.now(timezone.utc) + timedelta(hours=12)}
    return jwt.encode(payload, settings.app_secret_key, algorithm=ALGORITHM)
def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    if not creds: raise HTTPException(401, "Authentication required")
    try: payload = jwt.decode(creds.credentials, settings.app_secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError: raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, int(payload["sub"]))
    if not user: raise HTTPException(401, "User no longer exists")
    return user
def require_roles(*roles):
    def checker(user: User = Depends(current_user)):
        if user.role not in roles: raise HTTPException(403, "Insufficient permissions")
        return user
    return checker
