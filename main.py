from fastapi import FastAPI
from database import Base, engine
import models

from auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": "JWT Auth API running"}

print("NEW VERSION DEPLOYED")