from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4

import pytz
from sqlalchemy.orm import Mapped, mapped_column

from app.database.enums import UserRole
from app.database.session import Base


class User(Base):
    __tablename__: str = "users"

    guid: Mapped[UUID] = mapped_column(
        primary_key=True, unique=True, index=True, nullable=False, default=uuid4
    )
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_psw: Mapped[str] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now(tz=pytz.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now(tz=pytz.utc)
    )
    role: Mapped[UserRole] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=True)
    poste_code: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    county: Mapped[str] = mapped_column(nullable=True)
    country: Mapped[str] = mapped_column(nullable=True)
    age: Mapped[int] = mapped_column(nullable=True)
    date_of_birth: Mapped[str] = mapped_column(nullable=False)

    def dump(self) -> Dict[Any, Any]:
        return {field.name: getattr(self, field.name) for field in self.__table__.c}
