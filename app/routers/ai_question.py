from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Question
from app.llm.deepseek_client import generate_questions
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class AIQuestionRequest(BaseModel):
    topic: str  # 知识点，比如"Python基础"
    question_type: str  # single_choice / true_false
    difficulty: int  # 1-5
    count: Optional[int] = 1  # 生成几道题
    extra_requirements: Optional[str] = ""  # 额外要求

# AI自动出题接口
@router.post("/generate")
async def generate_ai_questions(
    request: AIQuestionRequest,
    db: Session = Depends(get_db)
):
    try:
        questions = await generate_questions(
            topic=request.topic,
            question_type=request.question_type,
            difficulty=request.difficulty,
            count=request.count,
            extra_requirements=request.extra_requirements
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI生成失败：{str(e)}")

    # 把生成的题目存入数据库
    saved = []
    for q in questions:
        # 转换题型格式
        type_map = {
            "single_choice": "single",
            "multiple_choice": "multiple",
            "true_false": "judge"
        }
        q_type = type_map.get(q["type"], "single")

        # 转换选项格式
        options = None
        if q["options"]:
            option_keys = ["A", "B", "C", "D"]
            options = {option_keys[i]: opt for i, opt in enumerate(q["options"]) if i < 4}

        new_question = Question(
            content=q["content"],
            type=q_type,
            options=options,
            answer=q["answer"],
            difficulty=request.difficulty,
            category=request.topic,
            created_by=1
        )
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        saved.append({
            "id": new_question.id,
            "content": new_question.content,
            "type": new_question.type,
            "options": new_question.options,
            "answer": new_question.answer,
            "analysis": q.get("analysis", "")
        })

    return {
        "message": f"成功生成{len(saved)}道题目",
        "questions": saved
    }