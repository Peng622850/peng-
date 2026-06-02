from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import User
from app.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from app.core import hash_password, verify_password, create_access_token

router = APIRouter()

# 注册接口
@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    # 创建新用户
    new_user = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        email=user_data.email,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 登录接口
@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # 查找用户
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 验证密码
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 生成 token
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}