from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from core.database import Base


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))  # Foreign key to User table

    # Relationship back to User
    author = relationship("User", back_populates="posts")
