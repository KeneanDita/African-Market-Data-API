from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str | None = Field(default=None, max_length=200)


class RegisterResponse(BaseModel):
    api_key: str
    tier: str
    rate_limit: str
    docs: str
    message: str


class RotateResponse(BaseModel):
    api_key: str
    key_prefix: str
    tier: str
    message: str


class MeResponse(BaseModel):
    email: str
    name: str | None
    key_prefix: str
    tier: str
    rate_limit: int
    requests_this_hour: int
    requests_remaining: int
    created_at: datetime | None
    last_seen_at: datetime | None
