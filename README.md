# FastAPIBig

FastAPIBig is a Python package built on FastAPI designed for structuring and managing large-scale FastAPI applications. It provides tools for project organization, database operations, API development, and more to help developers build maintainable and scalable applications.

## Key Features

- **Project Structure Management**: CLI commands for creating standardized project layouts with feature-based or type-based organization
- **ORM Layer**: High-level abstraction over SQLAlchemy for easier database operations
- **Organized API Development**: Structured approach to API development with class-based views and modular routing
- **Automated Route Registration**: Automatic discovery and loading of routes
- **Layered Logic Processing**: Pipeline approach for request processing (validation → pre-operation → operation → post-operation)
- **Dynamic CRUD Views**: Simplified CRUD operations with minimal boilerplate

## Installation

```bash
pip install FastAPIBig
```

## Quick Start

### Creating a New Project

```bash
python -m fastapi-admin createproject myproject
cd myproject
```

This creates a new project with the following structure:
- `core/`: Core project settings and configurations
- `apps/`: Directory for your application modules

### Creating an App

```bash
# Feature-based app structure (default)
python -m cli.py startapp users

# Type-based app structure
python -m cli.py startapp products --tb
```

#### Feature-based Structure

Organizes code by feature, with each feature containing its own models, routes, and schemas:

```
apps/
└── users/
    ├── __init__.py
    ├── models.py
    ├── routes.py
    ├── schemas.py
    └── tests.py
```

#### Type-based Structure

Organizes code by type, with models, routes, and schemas in separate directories:

```
apps/
├── models/
│   └── users.py
├── routes/
│   └── users.py
├── schemas/
│   └── users.py
└── tests/
    └── users.py
```

### Running Your Server

```bash
# Run with default settings
python -m cli.py runserver

# Run with custom settings
python -m cli.py runserver --host 0.0.0.0 --port 8080 --reload --workers 4
```

### Creating Database Tables

```bash
python -m cli.py createtables
```

## Database Operations with ORM

FastAPIBig provides a high-level ORM class that simplifies database operations. Here's an example of how to use it:

```python
from FastAPIBig.orm.base.base_model import ORM
from your_app.models import User

# Initialize the ORM with your model
user_orm = ORM(User)

# Create a new user
new_user = await user_orm.create(username="johndoe", email="john@example.com")

# Get user by ID
user = await user_orm.get(1)

# Update user
updated_user = await user_orm.update(1, email="newemail@example.com")

# Delete user
success = await user_orm.delete(1)

# Query with filters
users = await user_orm.filter(is_active=True)

# Get first matching record
admin = await user_orm.first(is_admin=True)

# Check if records exist
exists = await user_orm.exists(username="johndoe")

# Count records
count = await user_orm.count()
```

## API Development with Operations

FastAPIBig provides operation classes that simplify creating CRUD endpoints. These operations can be combined to create comprehensive API views.

### Available Operations

- `CreateOperation`: Handles POST requests to create resources
- `ListOperation`: Handles GET requests to list resources
- `RetrieveOperation`: Handles GET requests for a single resource
- `UpdateOperation`: Handles PUT/PATCH requests to update resources
- `DeleteOperation`: Handles DELETE requests to remove resources

### Basic Usage

```python
from FastAPIBig.views.apis.operations import CreateOperation, ListOperation, DeleteOperation
from .models import User
from .schemas import UserSchemaIn, UserSchemaOut

class UserView(CreateOperation, ListOperation, DeleteOperation):
    model = User
    schema_in = UserSchemaIn
    schema_out = UserSchemaOut
    methods = ["create", "list", "delete"]  # Define endpoints to expose
    include_router = True  # Auto-register with FastAPI
```

This automatically creates:
- `POST /users/` - Create a new user
- `GET /users/` - List all users
- `DELETE /users/{pk}/` - Delete a user

### Customizing Routes

You can customize the API route behavior:

```python
class PostView(CreateOperation, RetrieveOperation, DeleteOperation):
    model = Post
    schema_in = PostSchemaIn
    schema_out = PostSchemaOut
    methods = ["create", "get", "delete"] 
    prefix = "/blog-posts"  # Custom URL prefix
    tags = ["blog"]  # Swagger documentation tags
    include_router = True
```

### Custom Methods

You can add custom methods to your operations:

```python
class UserView(CreateOperation, ListOperation, DeleteOperation):
    model = User
    schema_in = UserSchemaIn
    schema_out = UserSchemaOut
    methods = ["create", "list", "delete"]
    post_methods = ["create_user"]  # Custom POST method
    get_methods = ["get_user"]      # Custom GET method
    include_router = True

    async def create_user(self, create_data: CreateUserSchema):
        """Custom user creation logic"""
        instance = await self._model.create(
            name=create_data.name, email=create_data.email
        )
        return self.schema_out.model_validate(instance.__dict__)

    async def get_user(self, pk: int):
        """Get user with related posts"""
        user = await self._model.select_related(id=pk, attrs=["posts"])
        return self.schema_out.model_validate(user.__dict__)
```

## Custom Routers

While FastAPIBig provides operations for common patterns, you can also create custom routers:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/custom-posts", tags=["custom-posts"])

@router.get("/")
async def read_posts():
    return {"message": "posts app"}

@router.get("/comments/")
async def read_comments():
    return {"message": "test comments"}
```

## Authentication Integration

FastAPIBig works seamlessly with FastAPI's authentication mechanisms:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token

# Use in your operation class
class SecurePostView(CreateOperation, RetrieveOperation):
    model = Post
    schema_in = PostSchemaIn
    schema_out = PostSchemaOut
    
    # Add authentication to all endpoints
    dependencies = [Depends(get_current_user)]
```

## Dependency Injection

FastAPIBig fully supports FastAPI's dependency injection system:

```python
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

class PostListWithParams(ListOperation):
    model = Post
    schema_out = PostSchemaOut
    
    async def list(self, params: CommonQueryParams = Depends()):
        """Custom list with query parameters"""
        results = await self._model.filter()
        # Apply filtering based on params
        filtered = [r for r in results[params.skip:params.skip+params.limit]]
        return [self.schema_out.model_validate(r.__dict__) for r in filtered]
```

## Complete Examples

### Posts API with Custom Router and Authentication

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from .models import Post
from .schemas import PostSchemaIn, PostSchemaOut
from FastAPIBig.views.apis.operations import (
    ListOperation,
    CreateOperation,
    RetrieveOperation,
    DeleteOperation,
)

# Custom router for additional endpoints
router = APIRouter(prefix="/custom-posts", tags=["custom-posts"])

@router.get("/")
async def read_posts():
    return {"message": "posts app"}

@router.get("/comments/")
async def read_comments():
    return {"message": "test comments"}

# Authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return token

# Common parameters for pagination
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

# Post create, retrieve, delete operations
class PostView(CreateOperation, RetrieveOperation, DeleteOperation):
    model = Post
    schema_in = PostSchemaIn
    schema_out = PostSchemaOut
    methods = ["create", "get", "delete"]
    include_router = True
    
    # Add authentication to these endpoints
    dependencies = [Depends(get_current_user)]

# Post listing operation
class PostList(ListOperation):
    model = Post
    schema_in = PostSchemaIn
    schema_out = PostSchemaOut
    methods = ["list"]
    include_router = True
    
    async def list(self, params: CommonQueryParams = Depends()):
        """List posts with pagination"""
        posts = await self._model.all()
        return [
            self.schema_out.model_validate(post.__dict__) 
            for post in posts[params.skip:params.skip+params.limit]
        ]
```

### Users API with Custom Methods

```python
from fastapi import APIRouter
from .models import User
from .schemas import UserSchemaIn, UserSchemaOut, CreateUserSchema
from FastAPIBig.views.apis.operations import (
    CreateOperation,
    ListOperation,
    DeleteOperation,
)

# Custom router for additional endpoints
router = APIRouter(prefix="/custom-users", tags=["custom-users"])

@router.get("/")
def read_users():
    return {"message": "users app"}

# User view with custom methods
class UserView(CreateOperation, ListOperation, DeleteOperation):
    model = User
    schema_in = UserSchemaIn
    schema_out = UserSchemaOut
    methods = ["create", "list", "delete"]
    post_methods = ["create_user"]  # Custom POST method
    get_methods = ["get_user"]      # Custom GET method
    prefix = "/new-users"           # Custom URL prefix
    tags = ["new-users"]            # Custom documentation tag
    include_router = True

    async def create_user(self, create_data: CreateUserSchema):
        """Custom user creation with specific fields"""
        instance = await self._model.create(
            name=create_data.name, email=create_data.email
        )
        return self.schema_out.model_validate(instance.__dict__)

    async def get_user(self, pk: int):
        """Get user with their related posts in one query"""
        user = await self._model.select_related(id=pk, attrs=["posts"])
        return self.schema_out.model_validate(user.__dict__)
```

## Project Structure

A typical FastAPIBig project has the following structure:

```
myproject/
├── core/
│   ├── __init__.py
│   ├── app.py
│   ├── database.py
│   ├── middlewares.py
│   └── settings.py
├── apps/
│   └── ... (your application modules)
├── __init__.py
└── cli.py
```

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.