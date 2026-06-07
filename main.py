from fastapi import FastAPI

from auth.auth import router as auth_router
from routers.expenses import router as expenses_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(expenses_router)