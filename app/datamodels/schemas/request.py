import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, StrictInt, StrictStr, field_validator

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
    first_name: StrictStr = Field(default=...)
    last_name: StrictStr = Field(default=...)
    email: EmailStr = Field(default=...)
    age: StrictInt | None = Field(default=None, ge=1)
    date_of_birth: StrictStr = Field(default=...)
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

    @field_validator("date_of_birth", mode="before")
    def validate_date_of_birth(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%d/%m/%Y")
        except ValueError:
            raise ValueError(
                "Date of birth must be in the format: DD/MM/YYYY and respect valid calendar dates"
            )
        return value

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
