from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String
from FastAPIBig.orm.base.base_model import DECLARATIVE_BASE


# Define the User model
class User(DECLARATIVE_BASE):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # Relationship to Post
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
