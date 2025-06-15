from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app.settings import SessionDep
from .models import UserCreate, UserRead, User, Token, CsrfToken, InvalidToken, UserLogin
from .password import password_manager
from .security import create_access_token, create_refresh_token, verify_token, generate_csrf_token
from sqlmodel import text, select
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import JWT_REFRESH_TOKEN_EXPIRE_DAYS
from .utils import get_user_by_email, create_user, store_csrf_token, is_token_invalid, invalidate_all_user_tokens, \
    invalidate_token, delete_csrf_tokens


limiter = Limiter(key_func=get_remote_address)
router = APIRouter()
router.limiter = limiter



@router.post("/register", response_model=Token)
@limiter.limit("5/minute")
async def register(request: Request, user: UserCreate, session: SessionDep):
    existing_user = get_user_by_email(user.email, session)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = create_user(user, session)
    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
    csrf_token = generate_csrf_token()
    store_csrf_token(db_user.id, csrf_token, session)

    response = Response()
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    return {"access_token": access_token, "token_type": "bearer", "csrf_token": csrf_token}


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, session: SessionDep, user: UserLogin):
    db_user = get_user_by_email(user.email, session)
    if not db_user or not password_manager.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
    csrf_token = generate_csrf_token()
    store_csrf_token(db_user.id, csrf_token, session)

    response = Response()
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    return {"access_token": access_token, "token_type": "bearer", "csrf_token": csrf_token}



@router.post("/refresh")
@limiter.limit("10/hour")
async def refresh_token(request: Request, response: Response, session: SessionDep):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")

    if is_token_invalid(token, session):  # Check if token is invalidated
        # Reuse detected: Invalidate all user tokens
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id:
            user = session.get(User, int(user_id))
            if user:
                invalidate_all_user_tokens(user.id, session)  # Deletes family here
        raise HTTPException(status_code=401, detail="Invalidated refresh token")


    payload = verify_token(token)  # Decode + validate signature + expiration
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Now we know who the user is!
    user = session.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    invalidate_token(token, user.id, session)
    access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    csrf_token = generate_csrf_token()
    store_csrf_token(user.id, csrf_token, session)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    return {"access_token": access_token, "token_type": "bearer", "csrf_token": csrf_token}



@router.post("/logout")
async def logout(request: Request, response: Response, session: SessionDep):
    token = request.cookies.get("refresh_token")
    if token:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id:
            user = session.get(User, int(user_id))
            if user:
                invalidate_token(token, user.id, session)
                delete_csrf_tokens(user.id, session)
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out"}