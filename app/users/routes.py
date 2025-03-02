from fastapi import APIRouter
from app.users.models import User
from app.users.schemas import UserSchemaIn, UserSchemaOut, CreateUserSchema
from views.apis.operations import APIView

router = APIRouter()


@router.get("/")
def read_users():
    return {"message": "users app"}


class UserView(APIView):
    model = User
    schema_in = UserSchemaIn
    schema_out = UserSchemaOut
    methods = ["create", "get", "list", "delete"]
    post_methods = ["create_user"]
    get_methods = ["get_user"]



    async def create_user(self, create_data: CreateUserSchema):
        instance = await self.model.objects.create(
            name=create_data.name, email=create_data.email
        )
        return self.schema_out.model_validate(instance.__dict__)

    async def get_user(self, pk: int):
        user = await self.model.objects.select_related(id=pk, attrs=["posts"])
        return self.schema_out.model_validate(user.__dict__)


router.include_router(UserView.as_router(prefix="/users", tags=["Users"]))
