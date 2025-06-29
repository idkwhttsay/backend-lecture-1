from datetime import timedelta
from typing import Annotated
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.models import Token, UserResponseDTO, User, UserDTO
from src.auth.service import create_access_token, authenticate_user, create_user, get_current_active_user
from src.config import settings
from src.database import SessionDep

router = APIRouter(prefix="/auth")

# TODO: add logic for refresh token and change logic of access token expiration

@router.post("/token")
async def login_for_access_token(
    user_data: UserDTO,
    session: SessionDep
) -> Token:
    user = authenticate_user(user_data.username, user_data.password, session=session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")

@router.post("/register", response_model=UserResponseDTO)
async def register_user(
    user_dto: UserDTO,
    session: SessionDep
):
    logging.info(f" User DTO: {user_dto}")
    user = create_user(user_dto, session)
    logging.info(f"Registered user: {user}")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    return user

@router.get("/me", response_model=UserResponseDTO)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user