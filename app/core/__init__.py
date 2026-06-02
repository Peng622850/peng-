from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

# 密码加密工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 配置
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """把明文密码加密成哈希值，存入数据库"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证用户输入的密码是否和数据库里的哈希值匹配"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """生成 JWT token，登录成功后返回给用户"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """解析 JWT token，验证用户身份"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# 告诉 FastAPI token 从哪个接口获取
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

def get_current_user(token: str = Depends(oauth2_scheme), db = None):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    return payload