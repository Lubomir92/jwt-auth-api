from fastapi import FastAPI
from database import Base, engine
import models
from auth import router as auth_router

# vytvorenie tabuliek
Base.metadata.create_all(bind=engine)

app = FastAPI(title="JWT Auth API")

# router
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "JWT Auth API running"}