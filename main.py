from fastapi import FastAPI
from database import Base, engine

import models
from auth import router as auth_router
from expenses import router as exp_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(exp_router)