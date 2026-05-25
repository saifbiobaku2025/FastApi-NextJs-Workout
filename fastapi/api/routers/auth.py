import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from sqlalchemy.exc import IntegrityError

from api.deps import db_dependency, hash_password, verify_password
from api.models import User
from api.schemas import Token, UserCreate, UserRead

load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ALGORITHM = os.getenv("AUTH_ALGORITHM")


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "user_id": user_id}
    expire = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_user(db: db_dependency, create_user_request: UserCreate):
    create_user_model = User(
        username=create_user_request.username,
        hashed_password=hash_password(create_user_request.password),
    )
    db.add(create_user_model)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )
    db.refresh(create_user_model)
    return create_user_model


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: db_dependency,
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user",
        )
    token = create_access_token(user.username, user.id, timedelta(minutes=29))
    return Token(access_token=token, token_type="bearer")
