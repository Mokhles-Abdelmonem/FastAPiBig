from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from core.database import Base


# Define the User model
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # Relationship to Post
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
