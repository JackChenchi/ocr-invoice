from pydantic import BaseModel


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class UserListResponse(BaseModel):
    items: list[UserResponse]
