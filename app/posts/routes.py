import functools
from fastapi import APIRouter
from typing import Type, List, Optional
from pydantic import BaseModel

from views.apis.base import APIView

router = APIRouter()


@router.get("/")
async def read_posts():
    return {"message": "posts app"}



class ItemSchema(BaseModel):
    id: int
    name: str

class ItemView(APIView):
    model = ItemSchema
    schema_out = ItemSchema
    methods = ["create", "get", "list", "delete"]  # Define what endpoints to expose

router.include_router(ItemView.as_router(prefix="/items"))
