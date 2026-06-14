from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import models
from database import get_db
import bcrypt
from core.config import SECRET_KEY, ALGORITHM

router = APIRouter()

# ---------------- CONFIG ----------------
ACCESS_EXPIRE_MINUTES = 60  # 🔥 zvýšené (15 min je problém pri debugovaní)
REFRESH_EXPIRE_DAYS = 7

bearer = HTTPBearer(auto_error=True)


# ---------------- PASSWORD ----------------
def hash_password(password: str):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(plain: str, hashed: str):
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8")
    )


# ---------------- JWT ----------------
def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES),
        "type": "access"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS),
        "type": "refresh"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ---------------- LOGIN MODEL ----------------
class LoginRequest(BaseModel):
    email: str
    password: str


# ---------------- REGISTER ----------------
@router.post("/register")
def register(
    email: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(models.User.email == email).first()

    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = models.User(
        email=email,
        password=hash_password(password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created"}


# ---------------- LOGIN ----------------
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    db.add(models.RefreshToken(
        token=refresh_token,
        user_id=user.id
    ))
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ---------------- FIXED AUTH ----------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
):
    try:
        token = credentials.credentials

        print("========== AUTH DEBUG ==========")
        print("TOKEN:", token)
        print("SECRET_KEY:", SECRET_KEY)
        print("ALGORITHM:", ALGORITHM)

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        print("PAYLOAD:", payload)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type"
            )

        email = payload.get("sub")

        if not email:
            raise HTTPException(
                status_code=401,
                detail="Missing subject"
            )

        return email

    except JWTError as e:
        print("JWT ERROR:", str(e))

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# ---------------- ME ----------------
@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"email": user}


# ---------------- REFRESH ----------------
@router.post("/refresh")
def refresh(refresh_token: str = Body(...), db: Session = Depends(get_db)):

    stored = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == refresh_token
    ).first()

    if not stored:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

    new_access = create_access_token({
        "sub": payload["sub"]
    })

    return {"access_token": new_access}


# ---------------- LOGOUT ----------------
@router.post("/logout")
def logout(refresh_token: str = Body(...), db: Session = Depends(get_db)):

    token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == refresh_token
    ).first()

    if token:
        db.delete(token)
        db.commit()

    return {"message": "logged out"}