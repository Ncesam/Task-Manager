from __future__ import annotations

from sqlalchemy import select, Sequence, Row, insert, delete
from sqlalchemy.exc import SQLAlchemyError

from app.backend.database.BaseModel import BaseModel
from app.backend.database.Connection import DataBaseSessionCreator
from app.backend.schemas.BaseSchema import BaseSchema
from app.backend.settings.exceptions import Status


class BaseDTO:
    model: BaseModel

    @classmethod
    async def selectByFilters(cls, **filters) -> Sequence[Row["_TP"]]:
        async with DataBaseSessionCreator() as session:
            stmt = select(cls.model).filter_by(**filters)
            result = await session.execute(stmt)
            return result.scalars().all()

    @classmethod
    async def selectOneOrNone(cls, **filters) -> Row["_TP"]:
        async with DataBaseSessionCreator() as session:
            stmt = select(cls.model).filter_by(**filters)
            result = await session.execute(stmt)
            return result.one_or_none()

    @classmethod
    async def insert(cls, data: BaseSchema):
        async with DataBaseSessionCreator() as session:
            try:
                stmt = insert(cls.model).values(**data.model_dump())
            except ValueError as error:
                return Status.ERROR
            try:
                await session.execute(stmt)
                await session.commit()
                return Status.OK
            except SQLAlchemyError as error:
                return Status.FAILED

    @classmethod
    async def deleteByFilters(cls, **filters):
        async with DataBaseSessionCreator() as session:
            try:
                stmt = delete(cls.model).filter_by(**filters)
            except ValueError as error:
                return Status.ERROR
            try:
                await session.execute(stmt)
                await session.commit()
                return Status.OK
            except SQLAlchemyError as error:
                return Status.FAILED
