from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
import auth

from database import engine, SessionLocal

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# =========================
# DATABASE SESSION
# =========================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

# =========================
# ROUTES
# =========================

@app.get("/")
def home():
    return {"message": "JWT Auth API running"}

# -------------------------
# REGISTER
# -------------------------

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed = auth.hash_password(user.password)

    new_user = models.User(
        email=user.email,
        hashed_password=hashed
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "user created"}

# -------------------------
# LOGIN
# -------------------------

@app.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    if not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Wrong password")

    token = auth.create_access_token({"sub": db_user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# -------------------------
# PROTECTED ROUTE
# -------------------------

@app.get("/protected")
def protected_route(
    current_user: str = Depends(auth.get_current_user)
):

    return {
        "message": "You are authenticated",
        "user": current_user
    }

# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)