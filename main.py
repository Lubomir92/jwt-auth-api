from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import engine

from auth.auth import router as auth_router
from routers.expenses import router as expenses_router

# ---------------- APP ----------------
app = FastAPI(title="JWT Auth API")

# ---------------- CORS ----------------
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://expense-tracker-frontend-five-xi.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- CREATE TABLES ----------------
models.Base.metadata.create_all(bind=engine)

# ---------------- ROUTERS ----------------
app.include_router(auth_router)
app.include_router(expenses_router)

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"message": "API is running"}