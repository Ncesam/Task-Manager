from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Form
from starlette.responses import JSONResponse

from app.backend.schemas.User import UserCreate, UserDelete, UserToDB, UserLogin
from app.backend.security.JWT import register_user, login_user
from app.backend.services.UserService import UserService
from app.backend.settings.exceptions import Status

router = APIRouter(prefix="/user", tags=['User Service'])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: Annotated[UserCreate, Form()]) -> str:
    prepared_user: UserToDB = register_user(user_data)
    response: str = await UserService.add_user(prepared_user)
    return response


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_data: Annotated[UserLogin, Form()], response: JSONResponse) -> dict:
    access_token: str = await login_user(user_data)
    response.set_cookie('access_token', access_token)
    return {"message": "Successful"}


@router.delete('')
async def delete_user(user_data: Annotated[UserDelete, Form()]):
    response = await UserService.delete_user(user_data=user_data)
    if response == Status.OK:
        return HTTPException(
            status_code=status.HTTP_200_OK)
    else:
        return {response}
