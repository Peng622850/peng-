from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# 用户注册时，前端传过来的数据格式
class UserRegister(BaseModel):
    username: str
    password: str
    email: str
    role: Optional[str] = "student"

# 用户登录时，前端传过来的数据格式
class UserLogin(BaseModel):
    username: str
    password: str

# 登录成功后，返回给前端的数据格式
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# 返回用户信息时的数据格式
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True

# 创建题目时，前端传过来的数据格式
class QuestionCreate(BaseModel):
    content: str
    type: str  # single / multiple / judge
    options: Optional[dict] = None
    answer: str
    difficulty: Optional[int] = 1
    category: Optional[str] = None

# 返回题目信息时的数据格式
class QuestionResponse(BaseModel):
    id: int
    content: str
    type: str
    options: Optional[dict] = None
    answer: str
    difficulty: int
    category: Optional[str] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

# 创建考试时，前端传过来的数据格式
class ExamCreate(BaseModel):
    title: str
    description: Optional[str] = None
    duration: int  # 考试时长，单位分钟
    total_score: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    question_ids: List[int]  # 题目id列表
    scores: List[int]  # 每道题对应的分值

# 返回考试信息时的数据格式
class ExamResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    duration: int
    total_score: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

# 学生提交答案时的数据格式
class SubmitAnswer(BaseModel):
    exam_id: int
    answers: dict  # 格式：{题目id: 答案}


class AIGenerateRequest(BaseModel):
    topic: str = Field(..., description="知识点或主题")
    question_type: str = Field(..., description="题目类型")
    difficulty: int = Field(..., ge=1, le=5, description="难度 1-5")
    count: int = Field(1, ge=1, le=5, description="生成数量，最多5道")
    extra_requirements: str = Field("", description="额外要求")

class AIGenerateResponse(BaseModel):
    success: bool
    created_questions: list = []   # 可以导入 QuestionResponse 并明确类型
    message: str = ""