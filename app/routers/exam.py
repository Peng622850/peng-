from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models import Exam, ExamQuestion, ExamRecord, AnswerDetail, Question
from app.schemas import ExamCreate, ExamResponse, SubmitAnswer
from app.routers.deps import get_current_user
from app.models import User

router = APIRouter()

@app.post("/", response_model=ExamResponse)
def create_exam(
    exam_data: ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if len(exam_data.question_ids) != len(exam_data.scores):
        raise HTTPException(status_code=400, detail="题目数量和分值数量不一致")

    new_exam = Exam(
        title=exam_data.title,
        description=exam_data.description,
        duration=exam_data.duration,
        total_score=exam_data.total_score,
        start_time=exam_data.start_time,
        end_time=exam_data.end_time,
        created_by=current_user.id
    )
    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)

    for question_id, score in zip(exam_data.question_ids, exam_data.scores):
        exam_question = ExamQuestion(
            exam_id=new_exam.id,
            question_id=question_id,
            score=score
        )
        db.add(exam_question)
    db.commit()
    return new_exam

@router.get("/", response_model=List[ExamResponse])
def get_exams(db: Session = Depends(get_db)):
    return db.query(Exam).all()

@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    return exam

@router.post("/{exam_id}/start")
def start_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")

    record = ExamRecord(
        exam_id=exam_id,
        user_id=current_user.id,
        status="ongoing"
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    exam_questions = db.query(ExamQuestion).filter(
        ExamQuestion.exam_id == exam_id
    ).all()

    questions = []
    for eq in exam_questions:
        question = db.query(Question).filter(Question.id == eq.question_id).first()
        questions.append({
            "question_id": question.id,
            "content": question.content,
            "type": question.type,
            "options": question.options,
            "score": eq.score
        })

    return {
        "record_id": record.id,
        "exam_title": exam.title,
        "duration": exam.duration,
        "questions": questions
    }

@router.post("/submit")
def submit_exam(
    submit_data: SubmitAnswer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    record = db.query(ExamRecord).filter(
        ExamRecord.exam_id == submit_data.exam_id,
        ExamRecord.user_id == current_user.id,
        ExamRecord.status == "ongoing"
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="考试记录不存在")

    total_score = 0
    for question_id_str, user_answer in submit_data.answers.items():
        question_id = int(question_id_str)
        question = db.query(Question).filter(Question.id == question_id).first()
        exam_question = db.query(ExamQuestion).filter(
            ExamQuestion.exam_id == submit_data.exam_id,
            ExamQuestion.question_id == question_id
        ).first()

        is_correct = question.answer.strip() == user_answer.strip()
        score_got = exam_question.score if is_correct else 0
        total_score += score_got

        detail = AnswerDetail(
            record_id=record.id,
            question_id=question_id,
            user_answer=user_answer,
            is_correct=is_correct,
            score_got=score_got
        )
        db.add(detail)

    from datetime import datetime
    record.submit_time = datetime.utcnow()
    record.total_score = total_score
    record.status = "submitted"
    db.commit()

    return {
        "message": "提交成功",
        "total_score": total_score,
        "full_score": db.query(Exam).filter(Exam.id == submit_data.exam_id).first().total_score
    }