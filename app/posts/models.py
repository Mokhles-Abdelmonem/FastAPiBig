from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from orm.base.base_model import DECLARATIVE_BASE


class Post(DECLARATIVE_BASE):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))  # Foreign key to User table

    # Relationship back to User
    author = relationship("User", back_populates="posts")
