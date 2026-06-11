from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict

import models
import schemas
from database import get_db
from auth.auth import get_current_user

from services.expense_service import (
    get_user_expenses,
    create_expense,
    get_top_expenses
)

router = APIRouter()


# ---------------- CREATE EXPENSE ----------------
@router.post("/expenses")
def create(
    expense: schemas.ExpenseCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db_user = db.query(models.User).filter(models.User.email == user).first()

    return create_expense(db, db_user.id, expense)


# ---------------- GET EXPENSES ----------------
@router.get("/expenses")
def get(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db_user = db.query(models.User).filter(models.User.email == user).first()

    return get_user_expenses(db, db_user.id)

# ---------------- UPDATE EXPENSE ----------------
@router.put("/expenses/{expense_id}")
def update_expense(
    expense_id: int,
    expense_data: schemas.ExpenseCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.email == user
    ).first()

    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == db_user.id
    ).first()

    if not expense:
        return {"error": "Expense not found"}

    expense.title = expense_data.title
    expense.amount = expense_data.amount
    expense.category = expense_data.category

    db.commit()
    db.refresh(expense)

    return expense


# ---------------- CATEGORY STATS ----------------
@router.get("/stats/category")
def by_category(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db_user = db.query(models.User).filter(models.User.email == user).first()

    expenses = get_user_expenses(db, db_user.id)

    stats = defaultdict(float)

    for e in expenses:
        stats[e.category] += e.amount

    return stats


# ---------------- TOTAL STATS ----------------
@router.get("/stats/total")
def total(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db_user = db.query(models.User).filter(models.User.email == user).first()

    expenses = get_user_expenses(db, db_user.id)

    return {
        "total_spent": sum(e.amount for e in expenses)
    }


# ---------------- TOP EXPENSES ----------------
@router.get("/stats/top")
def top_expenses(
    limit: int = 5,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db_user = db.query(models.User).filter(models.User.email == user).first()

    return get_top_expenses(db, db_user.id, limit)

# ---------------- DELETE EXPENSE ----------------
@router.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.email == user
    ).first()

    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == db_user.id
    ).first()

    if not expense:
        return {"error": "Expense not found"}

    db.delete(expense)
    db.commit()

    return {"message": "Deleted"}