from datetime import timedelta, datetime
from typing import Union

import bcrypt
import jwt
from fastapi import HTTPException
from sqlalchemy import Row

from app.backend.schemas.User import UserCreate, UserToDB, UserLogin
from app.backend.services.UserService import UserService
from app.backend.settings.settings import env_settings


def hash_password_generate(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_passwords(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def create_access_token(user_data: UserLogin) -> str:
    payload = {
        "email": user_data.email,
        'exp': datetime.utcnow() + timedelta(minutes=20)
    }
    return jwt.encode(payload=payload, key=env_settings.ALGORITHM_KEY, algorithm=env_settings.ALGORITHM)


def register_user(user_data: UserCreate) -> UserToDB:
    hashed_password = hash_password_generate(user_data.password)
    user = UserToDB(first_name=user_data.first_name, last_name=user_data.last_name, email=user_data.email,
                    hashed_password=hashed_password)
    return user


async def login_user(user_data: UserLogin) -> Union[HTTPException, str]:
    user = await check_user(user_data)
    if not user:
        raise HTTPException(200, "User not found")
    access_token: str = create_access_token(user_data)
    return access_token


async def check_user(user_data: UserLogin) -> Union[bool, Row]:
    user = await UserService.get_user(email=user_data.email)
    if type(user) is str:
        return False
    check_password: bool = verify_passwords(user_data.password, user.hashed_password)
    if not check_password:
        return False
    return user

def check_access_token(access_token: str) -> bool:
    payload = jwt.decode(jwt=access_token, algorithms=[env_settings.ALGORITHM], key=env_settings.ALGORITHM_KEY)
    if payload['exp'] < datetime.utcnow():
        raise HTTPException(403, "Token is expired")
    return True
