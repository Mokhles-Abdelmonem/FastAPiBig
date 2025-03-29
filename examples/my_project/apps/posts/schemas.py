from pydantic import BaseModel


# Input schema for creating or updating a Post
class PostSchemaIn(BaseModel):
    title: str
    content: str
    user_id: int  # Foreign key linking to User

    class Config:
        from_attributes = True  # Enable compatibility with SQLAlchemy models


class CustomPostSchemaIn(BaseModel):
    custom_title: str
    custom_content: str
    custom_user_id: int  # Foreign key linking to User

    class Config:
        from_attributes = True  # Enable compatibility with SQLAlchemy models


# Output schema for returning Post details
class PostSchemaOut(BaseModel):
    id: int
    title: str
    content: str
    user_id: int  # Foreign key linking to User

    class Config:
        from_attributes = True  # Enable compatibility with SQLAlchemy models
