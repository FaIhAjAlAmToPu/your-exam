from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import ForeignKey
from sqlmodel import Field, SQLModel
from pydantic import BaseModel, EmailStr

from app.config import JWT_REFRESH_TOKEN_EXPIRE_DAYS


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(..., unique=True, index=True)
    username: str = Field(...)
    password: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)

class CsrfToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(ForeignKey('user.id'), unique=True)
    token: str = Field(index=True)
    expires_at: datetime = Field(default=datetime.now()+timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS))

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str
    csrf_token: str

class InvalidToken(SQLModel, table=True):
    """To detect Token reuse"""
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True)
    user_id: int = Field(foreign_key="user.id")
    expires_at: datetime
