from pydantic import BaseModel, EmailStr

from src.conf.enums import Role


class RegisterBody(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: Role = Role.member


class LoginForm(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
