from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer


# Here Defined a Base instance
class Base(DeclarativeBase):
    id = Column(Integer, primary_key=True, autoincrement=True)
