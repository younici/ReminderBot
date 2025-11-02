from sqlalchemy import Column, Integer, Text, DateTime, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db.orm.base import Base

class QuoteRemind(Base):
    __tablename__ = "quotes_for_remind"

    id = Column(Integer, primary_key=True, autoincrement=True)

    time = Column(DateTime(timezone=True))
    timezone = Column(String, default="UTC")

    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(Text, nullable=False)

    is_send = Column(Boolean, default=False)

    user = relationship("User", back_populates="remind_list")