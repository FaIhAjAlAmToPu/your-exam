from datetime import datetime, timedelta

from fastapi import HTTPException
from pydantic import EmailStr
from sqlmodel import select

from app.auth.models import UserRead, User, UserCreate, CsrfToken, InvalidToken
from app.auth.password import password_manager
from app.config import JWT_REFRESH_TOKEN_EXPIRE_DAYS
from app.settings import SessionDep


def get_user_by_email(email: EmailStr, session: SessionDep) -> User|None:
    sql_statement = select(User).where(User.email == email)
    user = session.exec(sql_statement).first()
    return user

def create_user(user: UserCreate, session: SessionDep) -> UserRead:
    hashed_password = password_manager.hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return UserRead(id = db_user.id, email=db_user.email, username=db_user.username)

def store_csrf_token(user_id: int, token: str, session: SessionDep):
    db_token = CsrfToken(user_id=user_id, token=token)
    session.add(db_token)
    session.commit()

def get_csrf_token(token: str, session: SessionDep) -> CsrfToken:
    sql_statement = select(CsrfToken).where(CsrfToken.token == token)
    csrf = session.exec(sql_statement).first()
    if not csrf:
        raise HTTPException(status_code=404, detail="CSRF token not found")
    if csrf.expires_at > datetime.now():
        session.delete(csrf)
        session.commit()
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return csrf

def delete_csrf_tokens(user_id: int, session: SessionDep):
    session.query(CsrfToken).filter(CsrfToken.user_id == user_id).delete()
    session.commit()

def invalidate_token(token: str, user_id: int, session: SessionDep):
    expires_at = datetime.now() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = InvalidToken(token=token, user_id=user_id, expires_at=expires_at)
    session.add(db_token)
    session.commit()

def is_token_invalid(token: str, session: SessionDep) -> bool:
    return session.exec(select(InvalidToken).where(InvalidToken.token == token, InvalidToken.expires_at > datetime.now())).first() is not None

def invalidate_all_user_tokens(user_id: int, session: SessionDep):
    session.delete(session.exec(select(InvalidToken).where(InvalidToken.user_id == user_id)))
    session.delete(session.exec(select(CsrfToken).where(CsrfToken.user_id == user_id)))
    session.commit()