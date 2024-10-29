import http
import typing
import uuid

import pydantic
from flama import Flama, types
from flama.authentication import AuthenticationMiddleware, JWTComponent
from flama.authentication.jwt import JWT
from flama.http import APIResponse
from flama.middleware import Middleware

JWT_SECRET_KEY = uuid.UUID(int=0).bytes  # The secret key used to signed the token
JWT_HEADER_KEY = "Authorization"  # Authorization header identifie
JWT_HEADER_PREFIX = "Bearer"  # Bearer prefix
JWT_ALGORITHM = "HS256"  # Algorithm used to sign the token
JWT_TOKEN_EXPIRATION = 300  # 5 minutes in seconds
JWT_REFRESH_EXPIRATION = 2592000  # 30 days in seconds
JWT_ACCESS_COOKIE_KEY = "access_token"
JWT_REFRESH_COOKIE_KEY = "refresh_token"


class User(pydantic.BaseModel):
    id: uuid.UUID
    password: typing.Optional[str] = None


class UserToken(pydantic.BaseModel):
    id: uuid.UUID
    token: str


app = Flama(
    title="JWT protected API",
    version="1.0.0",
    description="JWT Authentication with Flama 🔥",
    docs="/docs/",
)

app.add_component(
    JWTComponent(
        secret=JWT_SECRET_KEY,
        header_key=JWT_HEADER_KEY,
        header_prefix=JWT_HEADER_PREFIX,
        cookie_key=JWT_ACCESS_COOKIE_KEY,
    )
)

app.add_middleware(
    Middleware(AuthenticationMiddleware),
)


@app.get("/public/info/", name="public-info")
def info():
    """
    tags:
        - Public
    summary:
        Info
    description:
        Returns a brief description of the API
    responses:
        200:
            description:
                Successful ping.
    """
    return {"title": app.schema.title, "description": app.schema.description, "public": True}


@app.post("/auth/", name="signin")
def signin(user: types.Schema[User]) -> types.Schema[UserToken]:
    """
    tags:
        - Public
    summary:
        Authenticate
    description:
        Returns a user token to access protected endpoints
    responses:
        200:
            description:
                Successful ping.
    """
    token = (
        JWT(
            header={"alg": JWT_ALGORITHM},
            payload={
                "iss": "vortico",
                "data": {"id": str(user["id"]), "permissions": ["my-permission-name"]},
            },
        )
        .encode(JWT_SECRET_KEY)
        .decode()
    )

    response = APIResponse(
        status_code=http.HTTPStatus.OK, schema=types.Schema[UserToken], content={"id": str(user["id"]), "token": token}
    )

    return response  # type: ignore[return-value]


@app.get("/private/info/", name="private-info", tags={"permissions": ["my-permission-name"]})
def protected_info():
    """
    tags:
        - Private
    summary:
        Info
    description:
        Returns a brief description of the API
    responses:
        200:
            description:
                Successful ping.
    """
    return {"title": app.schema.title, "description": app.schema.description, "public": False}
