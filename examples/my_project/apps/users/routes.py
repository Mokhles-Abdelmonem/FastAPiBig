from fastapi import APIRouter
from .models import User
from .schemas import UserSchemaIn, UserSchemaOut, CreateUserSchema
from FastAPIBig.views.apis.operations import (
    CreateOperation,
    ListOperation,
    DeleteOperation,
)

router = APIRouter(prefix="/custom-users", tags=["custom-users"])


@router.get("/")
def read_users():
    return {"message": "users app"}


class UserView(CreateOperation, ListOperation, DeleteOperation):
    model = User
    schema_in = UserSchemaIn
    schema_out = UserSchemaOut
    methods = ["create", "list", "delete"]
    post_methods = ["create_user"]
    get_methods = ["get_user"]
    prefix = "/new-users"
    tags = ["new-users"]

    include_router = True

    async def create_user(self, create_data: CreateUserSchema):
        instance = await self._model.create(
            name=create_data.name, email=create_data.email
        )
        return self.schema_out.model_validate(instance.__dict__)

    async def get_user(self, pk: int):
        user = await self._model.select_related(id=pk, attrs=["posts"])
        return self.schema_out.model_validate(user.__dict__)
