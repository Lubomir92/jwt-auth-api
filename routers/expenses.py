from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict

import models
import schemas
from database import get_db
from auth.auth import get_current_user
from services.expense_service import get_user_expenses, create_expense

router = APIRouter()


@router.post("/expenses")
def create(expense: schemas.ExpenseCreate,
           user=Depends(get_current_user),
           db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter_by(email=user).first()

    return create_expense(db, db_user.id, expense)


@router.get("/expenses")
def get(user=Depends(get_current_user),
        db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter_by(email=user).first()

    return get_user_expenses(db, db_user.id)


@router.get("/stats/category")
def by_category(user=Depends(get_current_user),
                db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter_by(email=user).first()

    expenses = get_user_expenses(db, db_user.id)

    stats = defaultdict(float)

    for e in expenses:
        stats[e.category] += e.amount

    return stats

@router.get("/stats/total")
def total(user=Depends(get_current_user),
          db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter_by(email=user).first()

    expenses = db.query(models.Expense).filter_by(
        user_id=db_user.id
    ).all()

    return {
        "total_spent": sum(e.amount for e in expenses)
    }