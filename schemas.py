from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str


class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str