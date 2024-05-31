from enum import Enum


class UserRole(Enum):
    admin: str = "ADMIN"
    viewer: str = "VIEWER"
