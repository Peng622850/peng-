from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接地址
# 格式：mysql+pymysql://用户名:密码@地址:端口/数据库名
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@localhost:3307/exam_system"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 所有模型的基类
Base = declarative_base()

# 获取数据库会话的依赖函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()