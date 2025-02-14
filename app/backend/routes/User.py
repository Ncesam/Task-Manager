from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Form
from starlette.responses import JSONResponse

from app.backend.schemas.User import UserCreate, UserDelete, UserToDB, UserLogin
from app.backend.security.JWT import Token
from app.backend.services.UserService import UserService
from app.backend.utilities.exceptions import Status

router = APIRouter(prefix="/user", tags=['User Service'])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: Annotated[UserCreate, Form()]):
    prepared_user: UserToDB = Token.prepare_new_user(user_data)
    response: Status = await UserService.add_user(prepared_user)
    if response is Status.ERROR:
        return {"message": "User just registered successfully"}
    refresh_token: str = Token.create_refresh_token(prepared_user.email)
    status = await Token.add_refresh_token(prepared_user.email, refresh_token)
    if status is Status.ERROR:
        return {"message": "Don't register this user"}
    return {"message": "Successful registration"}


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user_data: Annotated[UserLogin, Form()], response: JSONResponse) -> dict:
    access_token, refresh_token = await Token.login_user(user_data)
    response.set_cookie('access_token', access_token)
    response.set_cookie('refresh_token', refresh_token)
    return {"message": "Successful"}


@router.delete('')
async def delete_user(user_data: Annotated[UserDelete, Form()]):
    response = await UserService.delete_user(user_data=user_data)
    if response == Status.OK:
        return HTTPException(
            status_code=status.HTTP_200_OK)
    else:
        return {response}
