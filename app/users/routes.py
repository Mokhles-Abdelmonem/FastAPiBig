from fastapi import APIRouter
from pydantic import BaseModel
from orm.base.base_model import User
from views.apis.base import APIView

router = APIRouter()


@router.get("/")
def read_users():
    return {"message": "users app"}


class UserSchema(BaseModel):
    name: str
    email: str


class UserView(APIView):
    model = User
    schema_in = UserSchema
    schema_out = UserSchema
    methods = ["create", "get", "list", "delete"]  # Define what endpoints to expose

router.include_router(UserView.as_router(prefix="/users", tags=["Users"]))
