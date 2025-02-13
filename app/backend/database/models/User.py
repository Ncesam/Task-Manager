from __future__ import annotations

from typing import List, TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.backend.database.BaseModel import BaseModel

if TYPE_CHECKING:
    from app.backend.database.models.Task import Task


class User(BaseModel):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    tasks: Mapped[List["Task"]] = relationship(back_populates="user")
