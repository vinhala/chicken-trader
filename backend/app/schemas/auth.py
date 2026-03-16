from pydantic import BaseModel, EmailStr


DISCLAIMER_TEXT = (
    "This platform provides AI-generated informational content only. "
    "It does not provide actionable investment advice. "
    "Users are solely responsible for their own investment decisions. "
    "Information is provided as-is with no warranty of accuracy or completeness. "
    "The platform is not liable for trading losses or damages."
)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    disclaimer_accepted: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
