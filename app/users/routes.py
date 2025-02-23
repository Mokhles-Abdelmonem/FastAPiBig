from fastapi import APIRouter
from app.users.models import User
from app.users.schemas import UserSchemaIn, UserSchemaOut
from views.apis.base import APIView

router = APIRouter()


@router.get("/")
def read_users():
    return {"message": "users app"}



class UserView(APIView):
    model = User
    schema_in = UserSchemaIn
    schema_out = UserSchemaOut
    methods = ["create", "get", "list", "delete"]  # Define what endpoints to expose

    async def get(self, pk: int):
        user = await self.model.objects.select_related(id=pk,  attrs=["posts"])
        return self.schema_out.model_validate(user.__dict__)

router.include_router(UserView.as_router(prefix="/users", tags=["Users"]))
