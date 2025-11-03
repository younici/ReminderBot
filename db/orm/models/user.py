from typing import List

from db.orm.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped

from db.orm.models.remind_quote import QuoteRemind

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, primary_key=True)
    tg_id = Column(Integer, nullable=False, unique=True)

    timezone = Column(String, default="Europe/Kyiv")
    lang_code = Column(String, default="EN")

    remind_list: Mapped[List["QuoteRemind"]] = relationship(
        "QuoteRemind",
        back_populates="user",
        cascade="all, delete-orphan"
    )