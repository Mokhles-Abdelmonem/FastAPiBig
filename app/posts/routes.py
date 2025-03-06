from fastapi import APIRouter, Depends
from app.posts.models import Post
from app.posts.schemas import PostSchemaIn, PostSchemaOut
from views.apis.operations import APIView

router = APIRouter()


@router.get("/")
async def read_posts():
    return {"message": "posts app"}


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
    dependencies = [Depends(CommonQueryParams)]
    dependencies_by_method = {
        "list": [Depends(QueryParams)],
    }


router.include_router(PostView.as_router(prefix="/posts", tags=["Posts"]))
