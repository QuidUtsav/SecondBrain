# schemas/account.py

from pydantic import BaseModel, EmailStr


class AccountCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class AccountResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True