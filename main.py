from fastapi import FastAPI

import models
from database import engine
from auth import router as auth_router
from routers import expenses

# vytvorenie tabuliek
models.Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()

# root endpoint
@app.get("/")
def root():
    return {"message": "JWT Auth API running"}

# auth routes
app.include_router(auth_router)

# expense routes
app.include_router(expenses.router)