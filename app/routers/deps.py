from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db import get_db
from app.core import decode_token
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="token无效或已过期")

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
    return current_user