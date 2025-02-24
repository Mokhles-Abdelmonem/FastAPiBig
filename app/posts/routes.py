from fastapi import APIRouter
from app.posts.models import Post
from app.posts.schemas import PostSchemaIn, PostSchemaOut, CustomPostSchemaIn
from views.apis.base import APIView

router = APIRouter()


@router.get("/")
async def read_posts():
    return {"message": "posts app"}


class PostView(APIView):
    model = Post
    schema_in = PostSchemaIn
    schema_out = PostSchemaOut
    methods = ["create", "get", "list", "delete"]  # Define what endpoints to expose

    schemas_in = {"create": CustomPostSchemaIn}

    async def get(self, pk: int):
        post = await self.model.objects.get(pk=pk)
        return self.schema_out.model_validate(post.__dict__)

    async def list(self):
        instances = await self.model.objects.filter()
        return [
            self.schema_out.model_validate(instance.__dict__) for instance in instances
        ]


router.include_router(PostView.as_router(prefix="/posts", tags=["Posts"]))
