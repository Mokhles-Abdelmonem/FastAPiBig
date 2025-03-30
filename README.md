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
pip install fastapibig
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

## API Development

### Class-based Views

FastAPIBig supports class-based views for organizing your API endpoints:

```python
from FastAPIBig.views.apis.base import APIView
from fastapi import Depends

class UserAPI(APIView):
    path = "/users"
    tags = ["Users"]
    
    async def get(self):
        """Get all users"""
        users = await self.orm.all()
        return users
        
    async def post(self, user_data: UserCreate):
        """Create a new user"""
        # Validation is automatic based on the Pydantic model
        new_user = await self.orm.create(**user_data.dict())
        return new_user
```

### Layered Request Processing

FastAPIBig structures API logic into distinct phases:

1. **Validation**: Automatic validation using Pydantic models
2. **Pre-operation**: Execute logic before the main operation
3. **Operation**: Perform the core functionality
4. **Post-operation**: Execute logic after the main operation

Example:

```python
class UserAPI(APIView):
    path = "/users"
    
    async def pre_post(self, user_data):
        """Logic to run before creating a user"""
        # Check if email is already registered
        if await self.orm.exists(email=user_data.email):
            raise HTTPException(400, "Email already registered")
        
    async def post(self, user_data: UserCreate):
        """Create a new user"""
        new_user = await self.orm.create(**user_data.dict())
        return new_user
        
    async def post_post(self, user, user_data):
        """Logic to run after creating a user"""
        # Send welcome email
        await send_welcome_email(user.email)
```

## Advanced Usage

### Custom Database Session Management

```python
from FastAPIBig.orm.base.session_manager import DataBaseSessionManager
from FastAPIBig.orm.base.base_model import ORMSession

# Initialize the session manager
db_manager = DataBaseSessionManager("postgresql+asyncpg://user:pass@localhost/dbname")

# Initialize the ORM session
ORMSession.initialize(db_manager)
```

### Custom CLI Commands

You can extend the CLI with your own commands:

```python
from cli.py import cli
import click

@cli.command()
@click.argument("name")
def custom_command(name):
    """Custom CLI command"""
    click.echo(f"Hello, {name}!")
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