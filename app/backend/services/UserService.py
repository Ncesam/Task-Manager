import logging
from typing import Union

from sqlalchemy import Row

from app.backend.database.DTO import BaseDTO
from app.backend.models.User import User
from app.backend.schemas.User import UserDelete, UserDeleteHashed, UserToDB
from app.backend.utilities.exceptions import Status


class UserService(BaseDTO):
    model = User

    @classmethod
    async def get_user(cls, **filters) -> Union[Row, Status]:
        user: Row = await cls.selectOneOrNone(**filters)
        if not user:
            return Status.NOT_FOUND
        return user[0]

    @classmethod
    async def add_user(cls, user_data: UserToDB) -> str:
        result: Status = await cls.insert(user_data)
        return result

    @classmethod
    async def delete_user(cls, user_data: UserDelete) -> Status:
        user = await cls.get_user(email=user_data.email)
        data_to_delete = UserDeleteHashed(hashed_password=user.hashed_password, email=user.email)
        response: Status = await UserService.deleteByFilters(**data_to_delete.model_dump())
        return response

    @classmethod
    async def update_user(cls, user_email: str, **update_data) -> Status:
        status: Status = await cls.update(email=user_email, new_data={**update_data})
        if status is Status.ERROR:
            logging.error("Error updating user")
            return Status.ERROR
        return Status.OK

