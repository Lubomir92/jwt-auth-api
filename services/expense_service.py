import models
from sqlalchemy.orm import Session


# ---------------- GET USER EXPENSES ----------------
def get_user_expenses(db: Session, user_id: int):
    return db.query(models.Expense).filter(models.Expense.user_id == user_id).all()


# ---------------- CREATE EXPENSE ----------------
def create_expense(db: Session, user_id: int, expense):

    new_expense = models.Expense(
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        user_id=user_id
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense


# ---------------- TOTAL SPENDING ----------------
def get_total_spending(db: Session, user_id: int):

    expenses = db.query(models.Expense).filter(models.Expense.user_id == user_id).all()

    return sum(e.amount for e in expenses)


# ---------------- CATEGORY STATS ----------------
def get_category_stats(db: Session, user_id: int):

    expenses = db.query(models.Expense).filter(models.Expense.user_id == user_id).all()

    stats = {}

    for e in expenses:
        stats[e.category] = stats.get(e.category, 0) + e.amount

    return stats


# ---------------- TOP EXPENSES ----------------
def get_top_expenses(db: Session, user_id: int, limit: int = 5):

    expenses = db.query(models.Expense).filter(models.Expense.user_id == user_id).all()

    return sorted(expenses, key=lambda x: x.amount, reverse=True)[:limit]