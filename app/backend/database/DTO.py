from __future__ import annotations

import logging

from sqlalchemy import select, Sequence, Row, insert, delete, update
from sqlalchemy.exc import SQLAlchemyError

from app.backend.database.BaseModel import BaseModel
from app.backend.database.Connection import DataBaseSessionCreator
from app.backend.schemas.BaseSchema import BaseSchema
from app.backend.utilities.exceptions import Status


class BaseDTO:
    model: BaseModel

    @classmethod
    async def selectByFilters(cls, **filters) -> Sequence[Row["_TP"]]:
        async with DataBaseSessionCreator() as session:
            stmt = select(cls.model).filter_by(**filters)
            result = await session.execute(stmt)
            await session.close()
            return result.scalars().all()

    @classmethod
    async def selectOneOrNone(cls, **filters) -> Row["_TP"]:
        async with DataBaseSessionCreator() as session:
            stmt = select(cls.model).filter_by(**filters)
            result = await session.execute(stmt)
            await session.close()
            return result.one_or_none()

    @classmethod
    async def update(cls, new_data: dict, **filters) -> Status:
        async with DataBaseSessionCreator() as session:
            try:
                print(new_data)
                print(filters)
                stmt = update(cls.model).filter_by(**filters).values(**new_data)
            except ValueError as e:
                logging.error("Failed updating data")
                await session.close()
                return Status.ERROR
            try:
                await session.execute(stmt)
                await session.commit()
                logging.debug("Updated data")
                await session.close()
                return Status.OK
            except SQLAlchemyError as e:
                logging.error("SQLAlchemy error %s", e)
                await session.close()
                return Status.ERROR

    @classmethod
    async def insert(cls, data: BaseSchema) -> Status:
        async with DataBaseSessionCreator() as session:
            try:
                stmt = insert(cls.model).values(**data.model_dump())
            except ValueError as error:
                logging.error("Failed to insert data")
                await session.close()
                return Status.ERROR
            try:
                await session.execute(stmt)
                await session.commit()
                logging.debug("Inserted data")
                await session.close()
                return Status.OK
            except SQLAlchemyError as error:
                logging.error("SQLAlchemyError: %s", error)
                await session.close()
                return Status.ERROR

    @classmethod
    async def deleteByFilters(cls, **filters) -> Status:
        async with DataBaseSessionCreator() as session:
            try:
                stmt = delete(cls.model).filter_by(**filters)
            except ValueError as error:
                logging.error("Failed to delete data")
                await session.close()
                return Status.ERROR
            try:
                await session.execute(stmt)
                await session.commit()
                logging.debug("Deleted data")
                await session.close()
                return Status.OK
            except SQLAlchemyError as error:
                logging.error("SQLAlchemyError: %s", error)
                await session.close()
                return Status.ERROR
