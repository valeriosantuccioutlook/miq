from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    StrictStr,
    field_serializer,
)

from app.database.enums import UserRole


class UserResponseModel(BaseModel):
    guid: UUID = Field(default=...)
    name: StrictStr = Field(default=...)
    last_name: StrictStr = Field(default=...)
    email: EmailStr = Field(default=...)
    role: UserRole = Field(default=UserRole.admin)
    address: StrictStr | None = Field(default=None)
    poste_code: StrictStr | None = Field(default=None)
    city: StrictStr | None = Field(default=None)
    county: StrictStr | None = Field(default=None)
    country: StrictStr | None = Field(default=None)

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True

    @field_serializer("role")
    def enum_to_value(self, enum: UserRole) -> str:
        return enum.value

    @field_serializer("guid")
    def guit_to_str(self, guid: UUID) -> str:
        return str(guid)
