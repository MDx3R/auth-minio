from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: EmailStr
    password: str


class RegisterUserRequest(BaseModel):
    username: EmailStr
    password: str
