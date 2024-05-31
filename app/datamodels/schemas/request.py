import re

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    StrictStr,
    field_validator,
)

from app.database.enums import UserRole


class UserRequestBaseModel(BaseModel):
    address: StrictStr | None = Field(default=None)
    poste_code: StrictStr | None = Field(default=None)
    city: StrictStr | None = Field(default="Nottingham")
    county: StrictStr | None = Field(default="Nottinghamshire")
    country: StrictStr | None = Field(default="United Kingdom")
    role: UserRole = Field(default=UserRole.admin)

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True


class UserRequestModel(UserRequestBaseModel):
    name: StrictStr = Field(default=...)
    last_name: StrictStr = Field(default=...)
    email: EmailStr = Field(default=...)

    hashed_psw: StrictStr = Field(default=..., alias="password")

    @field_validator("hashed_psw", mode="before")
    def validate_psw(cls, value: str) -> str:
        if not re.match(
            pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
            string=value,
        ):
            raise ValueError(
                "Password must be longer then 10 characters, contain at least one upper case letter and one special character"
            )
        return value

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
