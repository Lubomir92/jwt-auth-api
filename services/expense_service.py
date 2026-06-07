import models
from sqlalchemy.orm import Session


def get_user_expenses(db: Session, user_id: int):
    """
    Vráti všetky expenses konkrétneho používateľa.
    """
    return db.query(models.Expense).filter_by(user_id=user_id).all()


def create_expense(db: Session, user_id: int, expense):
    """
    Vytvorí nový expense pre používateľa.
    """

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


def get_total_spending(db: Session, user_id: int):
    """
    Celková suma výdavkov používateľa.
    """

    expenses = db.query(models.Expense).filter_by(
        user_id=user_id
    ).all()

    return sum(e.amount for e in expenses)


def get_category_stats(db: Session, user_id: int):
    """
    Súčet výdavkov podľa kategórií.
    """

    expenses = db.query(models.Expense).filter_by(
        user_id=user_id
    ).all()

    stats = {}

    for expense in expenses:
        if expense.category not in stats:
            stats[expense.category] = 0

        stats[expense.category] += expense.amount

    return stats


def get_top_expenses(db: Session, user_id: int, limit: int = 5):
    """
    Najväčšie výdavky používateľa.
    """

    expenses = db.query(models.Expense).filter_by(
        user_id=user_id
    ).all()

    expenses.sort(
        key=lambda x: x.amount,
        reverse=True
    )

    return expenses[:limit]