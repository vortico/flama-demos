import typing
import uuid

import pydantic

__all__ = ["User", "UserCredentials", "UserDetails"]


class UserCredentials(pydantic.BaseModel):
    email: str
    password: str


class UserDetails(UserCredentials):
    name: str
    surname: str


class User(UserDetails):
    id: typing.Optional[uuid.UUID] = None
    active: typing.Optional[bool] = False
