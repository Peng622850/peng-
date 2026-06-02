from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import ExamRecord, AnswerDetail, Exam, Question

router = APIRouter()

# 查询个人成绩历史
@router.get("/my-records")
def get_my_records(db: Session = Depends(get_db)):
    records = db.query(ExamRecord).filter(
        ExamRecord.user_id == 1,  # 暂时写死
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

# 查询某场考试排行榜
@router.get("/exam/{exam_id}/ranking")
def get_exam_ranking(exam_id: int, db: Session = Depends(get_db)):
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

# 题目正确率统计
@router.get("/question-accuracy")
def get_question_accuracy(db: Session = Depends(get_db)):
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