from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel

from .models import Post
from .schemas import PostSchemaIn, PostSchemaOut
from FastAPIBig.views.apis.operations import APIView
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, List

from ..users.models import User

router = APIRouter(prefix="/custom-posts", tags=["custom-posts"])


@router.get("/")
async def read_posts():
    return {"message": "posts app"}


@router.get("/comments/")
async def read_comments():
    return {"message": "test comments"}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


class QueryParams:
    def __init__(self, q: str | None = None, skip: int = 0):
        self.q = q
        self.skip = skip


class PostView(APIView):
    model = Post
    schema_in = PostSchemaIn
    schema_out = PostSchemaOut
    methods = ["create", "get", "list", "delete"]  # Define what endpoints to expose
    dependencies_by_method = {
        "list": [Depends(QueryParams)],
    }
    include_router = True
