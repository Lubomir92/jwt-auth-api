from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta

import models
from database import get_db
from passlib.context import CryptContext
from core.config import SECRET_KEY, ALGORITHM

router = APIRouter()

ACCESS_EXPIRE_MINUTES = 15
REFRESH_EXPIRE_DAYS = 7

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()


# ---------------- PASSWORD ----------------
def verify_password(p, h):
    return pwd.verify(p, h)


# ---------------- TOKENS ----------------
def create_access_token(data: dict):
    payload = data.copy()
    payload.update({
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES),
        "type": "access"
    })
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    payload = data.copy()
    payload.update({
        "exp": datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS),
        "type": "refresh"
    })
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ---------------- LOGIN ----------------
@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):

    user = db.query(models.User).filter_by(email=form.username).first()

    if not user or not verify_password(form.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    access = create_access_token({"sub": user.email})
    refresh = create_refresh_token({"sub": user.email})

    db.add(models.RefreshToken(token=refresh, user_id=user.id))
    db.commit()

    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer"
    }


# ---------------- AUTH ----------------
def get_current_user(token=Depends(bearer)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "access":
            raise HTTPException(401, "Invalid token")

        return payload["sub"]

    except JWTError:
        raise HTTPException(401, "Invalid token")


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"email": user}


# ---------------- REFRESH ----------------
@router.post("/refresh")
def refresh(refresh_token: str = Body(...),
            db: Session = Depends(get_db)):

    stored = db.query(models.RefreshToken).filter_by(token=refresh_token).first()

    if not stored:
        raise HTTPException(401, "Invalid refresh token")

    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

    new_access = create_access_token({"sub": payload["sub"]})

    return {"access_token": new_access}


# ---------------- LOGOUT ----------------
@router.post("/logout")
def logout(refresh_token: str = Body(...),
           db: Session = Depends(get_db)):

    token = db.query(models.RefreshToken).filter_by(token=refresh_token).first()

    if token:
        db.delete(token)
        db.commit()

    return {"message": "logged out"}