from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel, TimestampedSchema
from app.schemas.role import RoleRead


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    email: EmailStr | None = None
    real_name: str = Field(min_length=2, max_length=50)
    gender: str
    major: str = Field(min_length=2, max_length=100)
    student_id: str = Field(min_length=4, max_length=50)


class UserLogin(BaseModel):
    identifier: str
    password: str


class UserProfileUpdate(BaseModel):
    email: EmailStr | None = None
    major: str | None = Field(default=None, max_length=100)
    gender: str | None = None
    real_name: str | None = Field(default=None, max_length=50)
    avatar: str | None = Field(default=None, max_length=255)


class UserRead(TimestampedSchema):
    id: int
    username: str
    email: EmailStr | None = None
    real_name: str
    gender: str
    major: str
    student_id: str
    avatar: str | None = None
    status: int
    verification_status: str
    roles: list[RoleRead] = []


class PublicUserRead(ORMModel):
    id: int
    username: str
    avatar: str | None = None
    verification_status: str
    roles: list[RoleRead] = []


class VerificationUpdate(BaseModel):
    verification_status: str


class RoleAssignment(BaseModel):
    role_ids: list[int]
