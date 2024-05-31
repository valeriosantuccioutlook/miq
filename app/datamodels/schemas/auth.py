from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, StrictInt, StrictStr


class Token(BaseModel):
    access_token: StrictStr = Field(default=...)
    token_type: StrictStr = Field(default=...)


class TokenData(BaseModel):
    email: EmailStr | None = Field(default=...)


class DecodedCredentials(BaseModel):
    email: EmailStr | None = Field(default=..., alias="sub")
    user_guid: UUID = Field(default=...)
    exp: StrictInt = Field(default=...)
