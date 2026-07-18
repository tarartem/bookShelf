from sqlalchemy.orm import Session
from backend.models import User, CreditTransaction

def award_upload_credits(db: Session, user_id: int, book_title: str):
    """
    Awards +1 credit to a user for a successful and approved book contribution.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    
    # Increment credits
    user.credits += 1
    
    # Log transaction
    transaction = CreditTransaction(
        user_id=user_id,
        amount=1,
        reason=f"Схвалено книгу: {book_title}"
    )
    db.add(transaction)
    
    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise e
