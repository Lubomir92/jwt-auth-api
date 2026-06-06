from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user

router = APIRouter()

@router.post("/expenses")
def create_expense(
    title: str,
    amount: float,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):

    exp = models.Expense(
        title=title,
        amount=amount,
        owner_email=user
    )

    db.add(exp)
    db.commit()

    return {"message": "created"}


@router.get("/expenses")
def get_expenses(
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):

    return db.query(models.Expense).filter_by(owner_email=user).all()