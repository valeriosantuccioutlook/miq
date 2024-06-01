from typing import Any, Dict
from uuid import uuid4

from app.database.enums import UserRole

CURRENT_AUTH_USER: Dict[str, Any] = {
    "role": UserRole.admin,
    "name": "mock_1",
    "last_name": "mock_1",
    "email": "mock@one.com",
    "hashed_psw": "TestTest123!",
}

MOCK_USER_1: Dict[str, Any] = {
    "role": "ADMIN",
    "name": "mock_1",
    "last_name": "mock_1",
    "email": "mock@one.com",
    "password": "TestTest123!",
}

MOCK_USER_2: Dict[str, Any] = {
    "role": "ADMIN",
    "name": "mock_2",
    "last_name": "mock_2",
    "email": "mock@two.com",
    "password": "TestTest123!",
}

MOCK_USER_3: Dict[str, Any] = {
    "guid": uuid4(),
    "role": "ADMIN",
    "name": "mock_3",
    "last_name": "mock_3",
    "email": "mock@three.com",
    "password": "TestTest123!",
}
