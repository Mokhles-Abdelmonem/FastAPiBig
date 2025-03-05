from functools import wraps
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type, Callable


def api_view(model: Type["ORM"]):
    """
    A decorator for handling common CRUD operations in FastAPI routes.
    - Detects CRUD type from function name (`create`, `get`, `update`, `delete`).
    - Uses SQLAlchemy ORM methods.
    - Injects async session automatically.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(
            *args,
            db_session: AsyncSession = Depends(model._db_manager.session),
            **kwargs
        ):
            operation = func.__name__.lower()

            operation_handlers = {
                "create": "create",
                "get": "get",
                "update": "update",
                "delete": "delete",
            }

            if operation == "create":
                instance = model(**kwargs)
                db_session.add(instance)
                await db_session.commit()
                await db_session.refresh(instance)
                return instance

            elif operation == "get":
                instance = await db_session.get(model, kwargs.get("id"))
                if not instance:
                    raise HTTPException(status_code=404, detail="Not found")
                return instance

            elif operation == "update":
                instance = await db_session.get(model, kwargs.get("id"))
                if not instance:
                    raise HTTPException(status_code=404, detail="Not found")
                for key, value in kwargs.items():
                    setattr(instance, key, value)
                await db_session.commit()
                await db_session.refresh(instance)
                return instance

            elif operation == "delete":
                instance = await db_session.get(model, kwargs.get("id"))
                if not instance:
                    raise HTTPException(status_code=404, detail="Not found")
                await db_session.delete(instance)
                await db_session.commit()
                return {"message": "Deleted successfully"}

            return await func(*args, **kwargs)  # Default to normal function execution

        return wrapper

    return decorator
