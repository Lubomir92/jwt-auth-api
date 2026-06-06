from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer

router = APIRouter()

SECRET_KEY = "secret123"
ALGORITHM = "HS256"
ACCESS_EXPIRE_MINUTES = 60

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

bearer = HTTPBearer()


# -------------------
# PASSWORD
# -------------------
def hash_password(p): return pwd.hash(p)
def verify_password(p, h): return pwd.verify(p, h)


# -------------------
# TOKEN
# -------------------
def create_token(data: dict):
    payload = data.copy()
    payload.update({
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    })
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# -------------------
# AUTH
# -------------------
def get_current_user(credentials=Depends(bearer)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(401, "Invalid token")
        return email
    except JWTError:
        raise HTTPException(401, "Invalid token")


# -------------------
# REGISTER
# -------------------
@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(400, "User exists")

    db.add(models.User(
        email=user.email,
        password=hash_password(user.password)
    ))
    db.commit()

    return {"message": "ok"}


# -------------------
# LOGIN (NO OAuth FORM)
# -------------------
@router.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"sub": db_user.email})

    return {"access_token": token, "token_type": "bearer"}


# -------------------
# TEST
# -------------------
@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"email": user}