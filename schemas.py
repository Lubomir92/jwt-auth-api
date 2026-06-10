from pydantic import BaseModel
from typing import Optional


# ---------------- USER ----------------
class UserCreate(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


# ---------------- LOGIN ----------------
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


# ---------------- EXPENSE ----------------
class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: Optional[str] = "general"


class ExpenseOut(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    user_id: int

    class Config:
        from_attributes = True