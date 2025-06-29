from pydantic import BaseModel, EmailStr
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserDTO(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None

class UserResponseDTO(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    full_name: str | None = None

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    username: str = Field(index=True, unique=True, max_length=50)
    email: EmailStr = Field(index=True, unique=True, max_length=50)
    full_name: str | None = Field(default=None, max_length=50)
    hashed_password: str = Field()
    disabled: bool | None = Field(default=False, nullable=True)
