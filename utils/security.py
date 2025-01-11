import time
from typing import Optional

import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from config import settings

PWD_CONTEXT = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl=settings.API_V1_PREFIX + '/auth/token')
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_ATK_EXPIRE = settings.JWT_ATK_EXP_DELTA
JWT_RTK_EXPIRE = settings.JWT_RTK_EXP_DELTA


def get_password_hash(password: str):
    return PWD_CONTEXT.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def create_atk(user_id: int):
    """创建访问令牌"""
    atk_exp = int(time.time() + JWT_ATK_EXPIRE)
    return jwt.encode(dict(sub=str(user_id), exp=atk_exp), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_rtk(user_id: int):
    """创建刷新令牌"""
    rtk_exp = int(time.time() + JWT_RTK_EXPIRE)
    return jwt.encode(dict(sub=str(user_id), exp=rtk_exp), JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_tk_pair(user_id: int):
    """创建访问令牌和刷新令牌"""
    return dict(access_token=create_atk(user_id), refresh_token=create_rtk(user_id))


def verify_token(token: str) -> Optional[int]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return int(payload.get('sub', None))
    except jwt.PyJWTError or ValueError:
        return None
