import hashlib
import http
import uuid

from flama import types
from flama.ddd.exceptions import NotFoundError
from flama.exceptions import HTTPException
from flama.http import APIResponse
from flama.resources import Resource, resource_method
from flama.resources.crud import CRUDResource

from src import models, schemas, worker

__all__ = ["AdminResource", "UserResource"]

ENCRYPTION_SALT = uuid.uuid4().hex
ENCRYPTION_PEPER = uuid.uuid4().hex


class Password:
    def __init__(self, password: str):
        self._password = password

    def encrypt(self):
        return hashlib.sha512(
            (hashlib.sha512((self._password + ENCRYPTION_SALT).encode()).hexdigest() + ENCRYPTION_PEPER).encode()
        ).hexdigest()


class AdminResource(CRUDResource):
    name = "admin"
    verbose_name = "Admin"

    model = models.user_table
    schema = schemas.User


class UserResource(Resource):
    name = "user"
    verbose_name = "User"

    @resource_method("/", methods=["POST"], name="create")
    async def create(self, worker: worker.RegisterWorker, data: types.Schema[schemas.UserDetails]):
        """
        tags:
            - User
        summary:
            User create
        description:
            Create a user
        responses:
            200:
                description:
                    User created in successfully.
        """
        async with worker:
            try:
                await worker.user.retrieve(email=data["email"])
            except NotFoundError:
                await worker.user.create({**data, "password": Password(data["password"]).encrypt(), "active": False})

        return APIResponse(status_code=http.HTTPStatus.OK)

    @resource_method("/signin/", methods=["POST"], name="signin")
    async def signin(self, worker: worker.RegisterWorker, data: types.Schema[schemas.UserCredentials]):
        """
        tags:
            - User
        summary:
            User sign in
        description:
            Create a user
        responses:
            200:
                description:
                    User signed in successfully.
            401:
                description:
                    User not active.
            404:
                description:
                    User not found.
        """
        async with worker:
            password = Password(data["password"])
            try:
                user = await worker.user.retrieve(email=data["email"])
            except NotFoundError:
                raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND)

            if user["password"] != password.encrypt():
                raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED)

            if not user["active"]:
                raise HTTPException(
                    status_code=http.HTTPStatus.BAD_REQUEST, detail=f"User must be activated via /user/activate/"
                )

        return APIResponse(status_code=http.HTTPStatus.OK, schema=types.Schema[schemas.User], content=user)

    @resource_method("/activate/", methods=["POST"], name="activate")
    async def activate(self, worker: worker.RegisterWorker, data: types.Schema[schemas.UserCredentials]):
        """
        tags:
            - User
        summary:
            User activate
        description:
            Activate an existing user
        responses:
            200:
                description:
                    User activated successfully.
            401:
                description:
                    User activation failed due to invalid credentials.
            404:
                description:
                    User not found.
        """
        async with worker:
            try:
                user = await worker.user.retrieve(email=data["email"])
            except NotFoundError:
                raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND)

            if user["password"] != Password(data["password"]).encrypt():
                raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED)

            if not user["active"]:
                await worker.user.update({**user, "active": True}, id=user["id"])

        return APIResponse(status_code=http.HTTPStatus.OK)

    @resource_method("/deactivate/", methods=["POST"], name="deactivate")
    async def deactivate(self, worker: worker.RegisterWorker, data: types.Schema[schemas.UserCredentials]):
        """
        tags:
            - User
        summary:
            User deactivate
        description:
            Deactivate an existing user
        responses:
            200:
                description:
                    User deactivated successfully.
            401:
                description:
                    User deactivation failed due to invalid credentials.
            404:
                description:
                    User not found.
        """
        async with worker:
            try:
                user = await worker.user.retrieve(email=data["email"])
            except NotFoundError:
                raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND)

            if user["password"] != Password(data["password"]).encrypt():
                raise HTTPException(status_code=http.HTTPStatus.UNAUTHORIZED)

            if user["active"]:
                await worker.user.update({**user, "active": False}, id=user["id"])

        return APIResponse(status_code=http.HTTPStatus.OK)
