from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from services.expense_service import create_expense, get_user_expenses, get_total, get_top
import models, schemas, auth
from database import get_db
from services import expense_service as service

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)

# =========================
# CREATE EXPENSE
# =========================

@router.post("/")
def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.get_current_user)
):

    db_user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()

    return service.create_expense(db, db_user, expense)


# =========================
# GET EXPENSES (FILTER + PAGINATION)
# =========================

@router.get("/")
def get_expenses(
    category: str = None,
    from_date: str = None,
    to_date: str = None,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.get_current_user)
):

    db_user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()

    query = service.get_user_expenses(db, db_user)

    # FILTER CATEGORY
    if category:
        query = query.filter(models.Expense.category == category)

    # FILTER DATE
    if from_date:
        query = query.filter(models.Expense.created_at >= from_date)

    if to_date:
        query = query.filter(models.Expense.created_at <= to_date)

    return query.offset(offset).limit(limit).all()


# =========================
# UPDATE EXPENSE
# =========================

@router.put("/{expense_id}")
def update_expense(
    expense_id: int,
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.get_current_user)
):

    db_user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()

    db_expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == db_user.id
    ).first()

    if not db_expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    db_expense.title = expense.title
    db_expense.amount = expense.amount
    db_expense.category = expense.category

    db.commit()
    db.refresh(db_expense)

    return db_expense


# =========================
# DELETE EXPENSE
# =========================

@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.get_current_user)
):

    db_user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()

    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == db_user.id
    ).first()

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    db.delete(expense)
    db.commit()

    return {"message": "Expense deleted"}


# =========================
# TOTAL SPENDING
# =========================

@router.get("/total")
def get_total(
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.get_current_user)
):

    db_user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()

    total = service.get_total(db, db_user)

    return {
        "user": db_user.email,
        "total_spent": total or 0
    }


# =========================
# CATEGORY STATS
# =========================

@router.get("/stats/categories")
def get_category_stats(
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.get_current_user)
):

    db_user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()

    stats = db.query(
        models.Expense.category,
        func.sum(models.Expense.amount)
    ).filter(
        models.Expense.user_id == db_user.id
    ).group_by(
        models.Expense.category
    ).all()

    return [
        {"category": category, "total": total}
        for category, total in stats
    ]


# =========================
# MONTHLY REPORT
# =========================

@router.get("/stats/monthly")
def monthly_report(
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.get_current_user)
):

    from datetime import datetime

    db_user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()

    now = datetime.utcnow()

    start_of_month = datetime(
        now.year,
        now.month,
        1
    )

    total = db.query(
        func.sum(models.Expense.amount)
    ).filter(
        models.Expense.user_id == db_user.id,
        models.Expense.created_at >= start_of_month
    ).scalar()

    return {
        "month": now.month,
        "year": now.year,
        "total_spent": total or 0
    }


# =========================
# TOP EXPENSE
# =========================

@router.get("/stats/top")
def top_expense(
    db: Session = Depends(get_db),
    current_user: str = Depends(auth.get_current_user)
):

    db_user = db.query(models.User).filter(
        models.User.email == current_user
    ).first()

    expense = service.get_top(db, db_user)

    if not expense:
        return {"message": "No expenses found"}

    return {
        "title": expense.title,
        "category": expense.category,
        "amount": expense.amount
    }