from typing import Optional, List

from app.backend.schemas.BaseSchema import BaseSchema


class UserBaseSchema(BaseSchema):
    first_name: str
    last_name: str
    email: str


class UserCreate(UserBaseSchema):
    password: str


class UserToDB(UserBaseSchema):
    hashed_password: str
    refresh_token: Optional[str] = None


class UserDB(UserBaseSchema):
    id: int
    hashed_password: str
    tasks: Optional[List["TaskBase"]] = None


class UserDelete(BaseSchema):
    email: str
    password: str


class UserDeleteHashed(BaseSchema):
    email: str
    hashed_password: str


class UserLogin(BaseSchema):
    email: str
    password: str
