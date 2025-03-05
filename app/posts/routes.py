from fastapi import APIRouter
from app.posts.models import Post
from app.posts.schemas import PostSchemaIn, PostSchemaOut
from views.apis.operations import APIView

router = APIRouter()


@router.get("/")
async def read_posts():
    return {"message": "posts app"}


class PostView(APIView):
    model = Post
    schema_in = PostSchemaIn
    schema_out = PostSchemaOut
    methods = ["create", "get", "list", "delete"]  # Define what endpoints to expose


router.include_router(PostView.as_router(prefix="/posts", tags=["Posts"]))
