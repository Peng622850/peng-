from fastapi import FastAPI
from app.db import engine, Base
from app.models import User, Question, Exam, ExamQuestion, ExamRecord, AnswerDetail
from app.routers import router
from app.routers.question import router as question_router
from app.routers.exam import router as exam_router
from app.routers.stats import router as stats_router
from app.routers.ai_question import router as ai_question_router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 创建 FastAPI 应用实例
app = FastAPI(title="在线考试系统", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/frontend")
def frontend():
    return FileResponse("static/index.html")

# 启动时自动创建所有数据库表
Base.metadata.create_all(bind=engine)

# 注册路由
app.include_router(router, prefix="/user", tags=["用户模块"])
app.include_router(question_router, prefix="/question", tags=["题库模块"])
app.include_router(exam_router, prefix="/exam", tags=["考试模块"])
app.include_router(stats_router, prefix="/stats", tags=["统计模块"])
app.include_router(ai_question_router, prefix="/ai", tags=["AI出题模块"])

@app.get("/")
def root():
    return {"message": "在线考试系统启动成功"}