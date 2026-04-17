from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Feedback
from backend.schemas import FeedbackCreate, FeedbackResponse

router = APIRouter()

@router.post("/", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackCreate, db: Session = Depends(get_db)):
    fb = Feedback(message=request.message)
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb

@router.get("/", response_model=list[FeedbackResponse])
def get_feedbacks(db: Session = Depends(get_db)):
    # To keep it simple, accessible without auth for demo purposes
    # In real app, put behind admin router.
    return db.query(Feedback).order_by(Feedback.created_at.desc()).all()
