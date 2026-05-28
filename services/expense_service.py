from sqlalchemy.orm import Session
import models


# =========================
# CREATE EXPENSE
# =========================

def create_expense(db: Session, user, expense):
    new_expense = models.Expense(
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        user_id=user.id
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense


# =========================
# GET EXPENSES
# =========================

def get_user_expenses(db: Session, user):
    return db.query(models.Expense).filter(
        models.Expense.user_id == user.id
    )


# =========================
# TOTAL
# =========================

def get_total(db: Session, user):
    return db.query(models.Expense).filter(
        models.Expense.user_id == user.id
    )


# =========================
# TOP EXPENSE
# =========================

def get_top(db: Session, user):
    return db.query(models.Expense).filter(
        models.Expense.user_id == user.id
    ).order_by(models.Expense.amount.desc()).first()