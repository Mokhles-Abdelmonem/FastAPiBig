from pydantic import BaseModel


class UserSchemaIn(BaseModel):
    name: str
    email: str

    class Config:
        from_attributes = True  # Enable compatibility with SQLAlchemy models


class CreateUserSchema(BaseModel):
    name: str
    email: str
    password: str

    class Config:
        from_attributes = True  # Enable compatibility with SQLAlchemy models


class UserSchemaOut(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True  # Enable compatibility with SQLAlchemy models
