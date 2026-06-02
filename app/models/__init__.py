from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db import Base

# 用户表
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(10), default="student")  # admin / student
    created_at = Column(DateTime, default=datetime.utcnow)

# 题目表
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(1000), nullable=False)
    type = Column(String(10), nullable=False)  # single / multiple / judge
    options = Column(JSON)  # 选项，判断题为空
    answer = Column(String(255), nullable=False)
    difficulty = Column(Integer, default=1)  # 1-5
    category = Column(String(50))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

# 考试表
class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    duration = Column(Integer, nullable=False)  # 分钟
    total_score = Column(Integer, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# 考试-题目关联表
class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    score = Column(Integer, nullable=False)  # 该题分值

# 考试记录表
class ExamRecord(Base):
    __tablename__ = "exam_records"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    submit_time = Column(DateTime)
    total_score = Column(Integer, default=0)
    status = Column(String(10), default="ongoing")  # ongoing / submitted

# 答题详情表
class AnswerDetail(Base):
    __tablename__ = "answer_details"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("exam_records.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    user_answer = Column(String(255))
    is_correct = Column(Boolean, default=False)
    score_got = Column(Integer, default=0)