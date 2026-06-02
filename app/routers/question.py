from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.models import Question
from app.schemas import QuestionCreate, QuestionResponse
from app.routers.deps import get_admin_user
from app.models import User

router = APIRouter()

# 添加题目接口
@router.post("/", response_model=QuestionResponse)
def create_question(
    question_data: QuestionCreate,
    db: Session = Depends(get_db)
):
    new_question = Question(
        content=question_data.content,
        type=question_data.type,
        options=question_data.options,
        answer=question_data.answer,
        difficulty=question_data.difficulty,
        category=question_data.category,
        created_by=1
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

# 获取题目列表接口
@router.get("/", response_model=List[QuestionResponse])
def get_questions(
    category: Optional[str] = None,
    difficulty: Optional[int] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Question)
    if category:
        query = query.filter(Question.category == category)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    if type:
        query = query.filter(Question.type == type)
    return query.all()

# 获取单个题目接口
@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    return question

# 删除题目接口
@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    db.delete(question)
    db.commit()
    return {"message": "题目删除成功"}