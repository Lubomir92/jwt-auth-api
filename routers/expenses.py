from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from collections import defaultdict

import models
import schemas
from database import get_db
from auth.auth import get_current_user

from services.expense_service import (
    get_user_expenses,
    create_expense,
)

router = APIRouter()


# ---------------- USER HELPER ----------------
def get_db_user(db: Session, email: str):
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# ---------------- CREATE EXPENSE ----------------
@router.post("/expenses")
def create(
    expense: schemas.ExpenseCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = get_db_user(db, user)
    return create_expense(db, db_user.id, expense)


# ---------------- GET EXPENSES ----------------
@router.get("/expenses")
def get(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = get_db_user(db, user)
    return get_user_expenses(db, db_user.id)


# ---------------- CATEGORY STATS (FIXED) ----------------
@router.get("/stats/category")
def by_category(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = get_db_user(db, user)

    expenses = db.query(models.Expense).filter(
        models.Expense.user_id == db_user.id
    ).all()

    stats = defaultdict(float)

    for e in expenses:
        stats[e.category] += float(e.amount)

    return dict(stats)


# ---------------- TOTAL STATS (FIXED + SAFE RETURN) ----------------
@router.get("/stats/total")
def total(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = get_db_user(db, user)

    expenses = db.query(models.Expense).filter(
        models.Expense.user_id == db_user.id
    ).all()

    total_sum = sum(float(e.amount) for e in expenses)

    return {
        "total_spent": total_sum
    }


# ---------------- DELETE EXPENSE ----------------
@router.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = get_db_user(db, user)

    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == db_user.id
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()

    return {"message": "Deleted"}