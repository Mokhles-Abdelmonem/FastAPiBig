from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_posts():
    return {"message": "posts app"}




FastAPIPro
class UserView(FastAPIView):
    _model = User
    _request_schema = UserIn
    _response_schema = UserIn

    def get_obj(self):
        return self._model

    def on_save(self, obj):
        return obj

    def on_update(self, obj):
        return obj

    def on_delete(self, obj):
        return obj

    def on_create(self, obj):
        return obj