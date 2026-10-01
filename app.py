from typing import Optional

from fastapi import (
    FastAPI, HTTPException, Query,
    Path, Header, Cookie, UploadFile,
    File, Form, Depends, status
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from pydantic import (
    BaseModel, Field, EmailStr
)
from enum import Enum

app = FastAPI(
    title='Пример Swagger',
    description='''
        Здесь будут примеры API:
        GET, POST, PUT, PATCH, DELETE
        Path parameters
        Query parameters
        Headers
        Cookies
        Json Body
        Form Data
        File upload
        Bearer Authorization
    ''',
    version='1.0.0'
)

users_db = [
    {
        'id': 1,
        'username': 'Andrey',
        'email': 'andrey@gmail.com',
        'age': 27,
        'address': 'Abaya 28/17346',
        'role': 'admin',
        'password': '123456'
    },
    {
        'id': 2,
        'username': 'Danil',
        'email': 'danil@gmail.com',
        'age': 30,
        'address': None,
        'role': 'user',
        'password': 'qwerty'
    },
    {
        'id': 3,
        'username': 'Aidar',
        'email': 'aidar@gmail.com',
        'age': 19,
        'address': 'Lenina 5',
        'role': 'moderator',
        'password': 'pass1234'
    },
]
class UserRole(str, Enum):
    user = 'user'
    admin = 'admin'
    moderator = 'moderator'

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        examples=['Andrey', 'Danil']
    )

    email: EmailStr

    age: int = Field(
        ..., 
        ge=18,
        le=100,
        examples=[27, 30, 19, 99]
    )

    address: Optional[str] | None = Field(
        None,
        examples=['Abaya 28/17346']
    )

    role: UserRole = UserRole.user

    password: str = Field(
        ...,
        min_length=6,
        max_length=32
    )

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    age: int
    role: Optional[UserRole] = None

class UserUpdate(BaseModel):
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=30
    )
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(
        None,
        ge=18,
        le=100
    )

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str



security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    if token != 'my_token_ahaha':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token'
        )

    return {
        'username': 'Andrey',
        'role': 'admin'
    }


@app.get(
    '/',
    tags=['General'],
    summary='главная страница'
)
def root():
    return {
        'message': 'FastApi работает',
        'docs': '/docs',
        'redoc': '/redoc',
        'openapi': '/openapi.json'
    }

@app.get(
    '/users',
    response_model=list[UserResponse],
    tags=['Users'],
    summary='получить список пользователей'
)
def get_users(
    role: Optional[UserRole] = Query(None, description='фильтр по роли'),
    email: Optional[str] = Query(None, description='фильтр по email'),
    age: Optional[int] = Query(None, description='фильтр по возрасту')
):
    result = users_db

    if role:
        result = [u for u in result if u['role'] == role.value]
    if email:
        result = [u for u in result if u['email'] == email]
    if age:
        result = [u for u in result if u['age'] == age]

    return result


@app.get(
    '/users/{user_id}',
    response_model=UserResponse,
    tags=['Users'],
    summary='получить пользователя',
)
def get_user(
    user_id: int = Path(..., ge=1, description='ID пользователя')
):
    for user in users_db:
        if user['id'] == user_id:
            return user

    raise HTTPException(
        status_code=404,
        detail='user not found'
    )

@app.post(
    '/users/create',
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=['Users'],
    summary='создать пользователя'
)
def create_user(user: UserCreate):
    new_user = user.model_dump()
    new_user['role'] = user.role.value
    new_user['id'] = len(users_db) + 1

    users_db.append(new_user)

    return new_user
