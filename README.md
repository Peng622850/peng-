# 在线考试系统（AI 增强版）

基于 FastAPI + DeepSeek 的在线考试系统，支持 AI 自动出题、自动判分、成绩统计等功能。

## 技术栈

- **后端框架**：FastAPI
- **数据库**：MySQL + SQLAlchemy ORM
- **身份认证**：JWT（JSON Web Token）
- **AI 能力**：DeepSeek API（自动出题）
- **服务器**：Uvicorn

## 项目亮点

- 集成 DeepSeek 大模型，支持按知识点、题型、难度 AI 自动出题并存入题库
- JWT 鉴权 + 角色权限控制（管理员 / 考生）
- 自动判分引擎，支持单选题、多选题、判断题
- 完整的 RESTful API 设计，FastAPI 自动生成 Swagger 文档

## 功能模块

| 模块 | 功能 |
|------|------|
| 用户模块 | 注册、登录、JWT鉴权、角色管理 |
| 题库模块 | 题目增删查、按分类/难度/题型筛选 |
| AI出题模块 | 调用 DeepSeek API 自动生成题目 |
| 考试模块 | 创建考试、开始考试、提交答案、自动判分 |
| 统计模块 | 个人成绩历史、考试排行榜、题目正确率 |

## 数据库设计

共 6 张表：`users`、`questions`、`exams`、`exam_questions`、`exam_records`、`answer_details`

## 快速启动

**1. 安装依赖**
pip install -r requirements.txt
2. 配置环境变量
在项目根目录创建 .env 文件：
DEEPSEEK_API_KEY=你的API Key
DEEPSEEK_BASE_URL=https://api.siliconflow.cn/v1
DEEPSEEK_MODEL=deepseek-ai/DeepSeek-V3
3. 配置数据库
在 app/db/__init__.py 中修改数据库连接：
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://用户名:密码@localhost:端口/exam_system"
4. 启动服务
uvicorn main:app --reload
5. 访问接口文档
http://127.0.0.1:8000/docs

接口概览:
POST   /user/register          用户注册
POST   /user/login             用户登录
POST   /question/              添加题目
GET    /question/              获取题目列表
POST   /ai/generate            AI自动出题
POST   /exam/                  创建考试
POST   /exam/{id}/start        开始考试
POST   /exam/submit            提交答案
GET    /stats/my-records       个人成绩历史
GET    /stats/exam/{id}/ranking 考试排行榜
GET    /stats/question-accuracy 题目正确率
