from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.database.BaseModel import BaseModel

if TYPE_CHECKING:
    from app.backend.database.models.User import User


class Task(BaseModel):
    __tablename__ = 'Tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(length=50))
    description: Mapped[str] = mapped_column(String(length=250))
    user_id: Mapped[int] = mapped_column(ForeignKey('Users.id'))
    user: Mapped["User"] = relationship(back_populates="tasks")
