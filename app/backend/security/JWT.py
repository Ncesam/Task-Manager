import logging
from datetime import timedelta, datetime
from typing import Union

import bcrypt
import jwt
from sqlalchemy import Row

from app.backend.schemas.User import UserCreate, UserToDB, UserLogin
from app.backend.services.UserService import UserService
from app.backend.utilities.exceptions import Status
from app.backend.utilities.settings import env_settings


class Token:

    @staticmethod
    def hash_password_generate(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_passwords(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    @staticmethod
    def prepare_new_user(user_data: UserCreate) -> UserToDB:
        hashed_password: str = Token.hash_password_generate(user_data.password)
        user = UserToDB(first_name=user_data.first_name, last_name=user_data.last_name, email=user_data.email,
                        hashed_password=hashed_password)
        return user

    @staticmethod
    async def login_user(user_data: UserLogin) -> Union[Status, tuple[str, str]]:
        user: Union[Row, Status] = await Token.check_user(user_data)
        if isinstance(user, Status):
            logging.debug("User isn't logged in")
            return Status.NOT_FOUND
        refresh_token: Union[Status, str] = await Token.get_refresh_token(user_email=user.email)
        if refresh_token is Status.INVALID:
            refresh_token: str = Token.create_refresh_token(user_email=user.email)
            await Token.add_refresh_token(user.email, refresh_token)
        access_token, refresh_token= await Token.create_access_token(user_data, refresh_token=refresh_token)
        logging.debug("User is logged in")
        return access_token, refresh_token

    @staticmethod
    async def check_user(user_data: UserLogin) -> Union[Status, Row]:
        user = await UserService.get_user(email=user_data.email)
        if user is Status.NOT_FOUND:
            logging.debug(f"User not found")
            return Status.NOT_FOUND
        logging.debug(f"User {user_data.email} found")
        check_password: bool = Token.verify_passwords(user_data.password, user.hashed_password)
        if not check_password:
            logging.debug(f"User {user_data.email} password invalid")
            return Status.INVALID
        logging.debug(f"User {user_data.email} is valid")
        return user

    @staticmethod
    async def update_refresh_token(user_email: str) -> str:
        refresh_token: str = Token.create_refresh_token(user_email=user_email)
        await Token.add_refresh_token(user_email=user_email, refresh_token=refresh_token)
        return refresh_token

    @staticmethod
    async def create_access_token(user_data: UserLogin, refresh_token: str) -> tuple[str, str]:
        if await Token.check_refresh_token(refresh_token) is Status.INVALID:
            refresh_token: str = await Token.update_refresh_token(user_data.email)
        payload = {
            "email": user_data.email,
            'exp': datetime.utcnow() + timedelta(minutes=20)
        }
        access_token = jwt.encode(payload=payload, key=env_settings.ALGORITHM_KEY, algorithm=env_settings.ALGORITHM)

        return access_token, refresh_token

    @staticmethod
    def check_access_token(access_token: str) -> bool:
        payload = jwt.decode(jwt=access_token, algorithms=[env_settings.ALGORITHM], key=env_settings.ALGORITHM_KEY)
        if datetime.fromtimestamp(payload['exp']) < datetime.utcnow():
            logging.debug("Access token expired")
            return False
        logging.debug("Access token is valid")
        return True

    @staticmethod
    def create_refresh_token(user_email: str) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=30),
            "email": user_email,
        }
        try:
            refresh_token = jwt.encode(payload, env_settings.ALGORITHM_KEY, algorithm=env_settings.ALGORITHM)
            logging.debug(f"Created new refresh token")
            return refresh_token
        except jwt.PyJWTError as error:
            logging.error("Error creating refresh token:", error)

    @staticmethod
    async def add_refresh_token(user_email: str, refresh_token: str) -> Status:
        await UserService.update_user(user_email=user_email, refresh_token=refresh_token)
        return Status.OK

    @staticmethod
    async def check_refresh_token(refresh_token: str) -> Status:
        user: Union[Row, Status] = await UserService.get_user(refresh_token=refresh_token)
        if user is Status.NOT_FOUND:
            logging.debug("User with this token not found")
            return Status.NOT_FOUND
        payload = jwt.decode(refresh_token, key=env_settings.ALGORITHM_KEY, algorithms=[env_settings.ALGORITHM])
        if datetime.fromtimestamp(payload['exp']) < datetime.utcnow():
            logging.debug("Refresh token expired")
            return Status.EXPIRED
        return Status.OK

    @staticmethod
    async def get_refresh_token(user_email: str) -> Union[Status, str]:
        user: Union[Row, Status] = await UserService.get_user(email=user_email)
        if user is Status.NOT_FOUND:
            logging.debug("User with this email not found")
            return Status.NOT_FOUND
        refresh_token = user.refresh_token
        if await Token.check_refresh_token(refresh_token):
            logging.debug("Refresh token is valid")
            return refresh_token
        logging.debug("Refresh token is invalid")
        return Status.INVALID
