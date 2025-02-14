from __future__ import annotations

from typing import List

from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.backend.database.BaseModel import BaseModel



class User(BaseModel):
    __tablename__ = 'Users'

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    tasks: Mapped[List["Task"]] = relationship(back_populates="user")
    refresh_token: Mapped[str] = mapped_column(nullable=True)

from app.backend.models.Task import Task