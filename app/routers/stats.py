from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import ExamRecord, AnswerDetail, Exam, Question, User
from app.routers.deps import get_current_user

router = APIRouter()

@router.get("/my-records")
def get_my_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = db.query(ExamRecord).filter(
        ExamRecord.user_id == current_user.id,
        ExamRecord.status == "submitted"
    ).all()

    result = []
    for record in records:
        exam = db.query(Exam).filter(Exam.id == record.exam_id).first()
        result.append({
            "record_id": record.id,
            "exam_title": exam.title,
            "total_score": record.total_score,
            "full_score": exam.total_score,
            "submit_time": record.submit_time
        })
    return result

@router.get("/exam/{exam_id}/ranking")
def get_exam_ranking(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    records = db.query(ExamRecord).filter(
        ExamRecord.exam_id == exam_id,
        ExamRecord.status == "submitted"
    ).order_by(ExamRecord.total_score.desc()).all()

    result = []
    for rank, record in enumerate(records, start=1):
        result.append({
            "rank": rank,
            "user_id": record.user_id,
            "total_score": record.total_score,
            "submit_time": record.submit_time
        })
    return result

@router.get("/question-accuracy")
def get_question_accuracy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    questions = db.query(Question).all()
    result = []
    for question in questions:
        details = db.query(AnswerDetail).filter(
            AnswerDetail.question_id == question.id
        ).all()
        total = len(details)
        correct = sum(1 for d in details if d.is_correct)
        accuracy = round(correct / total * 100, 2) if total > 0 else 0
        result.append({
            "question_id": question.id,
            "content": question.content,
            "total_attempts": total,
            "correct_count": correct,
            "accuracy": f"{accuracy}%"
        })
    return result