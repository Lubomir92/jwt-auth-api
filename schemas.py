from pydantic import BaseModel

# =========================
# USER SCHEMA
# =========================

class UserCreate(BaseModel):
    email: str
    password: str

# =========================
# EXPENSE SCHEMA
# =========================

class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str