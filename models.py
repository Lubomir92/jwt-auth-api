from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

# =========================
# USER TABLE
# =========================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# =========================
# EXPENSE TABLE
# =========================

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String)
    amount = Column(Float)
    category = Column(String)

    # owner expense
    user_id = Column(Integer, ForeignKey("users.id"))