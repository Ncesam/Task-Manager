from typing import Union

from sqlalchemy import Row

from app.backend.database.DTO import BaseDTO
from app.backend.database.models.User import User
from app.backend.schemas.User import UserDelete, UserDeleteHashed, UserToDB
from app.backend.settings.exceptions import Status


class UserService(BaseDTO):
    model = User

    @classmethod
    async def get_user(cls, **filters) -> Union[Row, str]:
        user: Row = await cls.selectOneOrNone(**filters)
        if not user:
            return "User not found"
        return user[0]

    @classmethod
    async def add_user(cls, user_data: UserToDB) -> str:
        result: Status = await cls.insert(user_data)
        if result == Status.OK:
            return "User added"
        return "User already exists"

    @classmethod
    async def delete_user(cls, user_data: UserDelete) -> Status:
        user = await cls.get_user(email=user_data.email)
        data_to_delete = UserDeleteHashed(hashed_password=user.hashed_password, email=user.email)
        response: Status = await UserService.deleteByFilters(**data_to_delete.model_dump())
        return response
