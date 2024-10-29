# Introducing Flama 1.7: Support for JWT Authentication

You've probably already heard about the recent release of [Flama 1.7](https://dev.to/vortico/releasing-flama-17-3n78), which brought some exciting new features to help you with the development and productionalisation of your ML APIs. This post is precisely devoted to one of the main highlights of that release: **Support for JWT Authentication**. But, before we dive into the details with a hands-on example, we recommend you to bear in mind the following resources (and, get familiar with them if you haven't already):

- Official Flama documentation: [Flama documentation](https://flama.dev/docs/)
- Post introducing Flama for ML APIs: [Introduction to Flama for Robust Machine Learning APIs](https://dev.to/vortico/introducing-flama-for-robust-machine-learning-apis-b3n)

Now, let's get started with the new feature and see how you can secure your API endpoints with token-based authentication over headers or cookies.

## Table of contents

This post is structured as follows:

- [What is JSON Web Token (JWT)?](#what-is-json-web-token)
- [JWT Authentication with Flama](#implementing-jwt-authentication-with-flama)
  - [Set up the development environment](#setting-up-the-development-environment)
  - [Base application](#base-application)
  - [Flama JWT Component](#authentication-flama-jwt-component)
  - [Protected endpoint](#adding-a-protected-endpoint)
  - [Running the application](#running-the-application)
  - [Login endpoint](#adding-the-login-endpoint)
- [Conclusions](#conclusions)
- [Support our work](#support-our-work)
- [References](#references)
- [About the authors](#about-the-authors)

## What is JSON Web Token?

If you're already familiar with the concept of JSON Web Token (JWT) and how it works, feel free to skip this section and jump straight to [Implementing JWT Authentication with Flama](#implementing-jwt-authentication-with-flama). Otherwise, we're going to try to provide you with a succinct explanation of what JWT is and why it's so useful for authorisation purposes.

### Brief introduction

We can start with the official definition given in the [RFC 7519](https://datatracker.ietf.org/doc/html/rfc7519) document:

> JSON Web Token (JWT) is a compact, URL-safe means of representing
   claims to be transferred between two parties.  The claims in a JWT
   are encoded as a JSON object that is used as the payload of a JSON
   Web Signature (JWS) structure or as the plaintext of a JSON Web
   Encryption (JWE) structure, enabling the claims to be digitally
   signed or integrity protected with a Message Authentication Code
   (MAC) and/or encrypted.


So, in simple terms, JWT is an open standard that defines a way for transmitting information between two parties in the form of a JSON object. The information being transmitted is digitally signed to ensure its integrity and authenticity. This is why one of the main use cases of JWT is for authorisation purposes. 

A prototypical JWT-based authentication flow would look something like this:

- A user logs in to a system and receives a JWT token.
- The user sends this token with every subsequent request to the server.
- The server verifies the token and grants access to the requested resource if the token is valid.
- If the token is invalid, the server denies access to the resource.

However, JWT tokens are not only useful to identify users, but they can also be used to share information between different services in a secure way via the payload of the token. Besides, given that the signature of the token is calculated using the header and the payload, the receiver can verify the integrity of the token and ensure that it hasn't been altered in transit.

### JWT Structure

A JWT is represented as a sequence of URL-safe parts separated by dots (`.`), with each part containing a base64url-encoded JSON object. The number of parts in the JWT can vary depending on the representation being used, either JWS (JSON Web Signature) [RFC-7515](https://datatracker.ietf.org/doc/html/rfc7515) or JWE (JSON Web Encryption) [RFC-7516](https://datatracker.ietf.org/doc/html/rfc7516). 
As of this point, we can assume we'll be using JWS, which is the most common representation for JWT tokens. In this case, a JWT token consists of three parts:

- **Header**: Contains metadata about the token and the cryptographic operations applied to it. 
- **Payload**: Contains the claims (information) that the token is carrying.
- **Signature**: Ensures the integrity of the token and is used to verify that the sender of the token is who it claims to be.

Thus, the syntax of a prototypical JWS JSON using the flattened JWS JSON Serialization is as follows (for more info, see [RFC-7515 Sec. 7.2.2](https://datatracker.ietf.org/doc/html/rfc7515#section-7.2.2)):

```
{
   "payload":"<payload contents>",
   "header":<header contents>,
   "signature":"<signature contents>"
}
```

In the JWS Compact Serialization, the JTW is represented as the  concatenation:

```
BASE64URL(UTF8(JWS Header)) || '.' || BASE64URL(JWS Payload) || '.' || BASE64URL(JWS Signature)  
```
An example of a JWT token would look like this (taken from one of the Flama tests [here](https://github.com/vortico/flama/blob/7b79ae4b38efefc0fb02223a4a2fcb13837283af/tests/authentication/test_jwt.py#L11)):

```
eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJkYXRhIjogeyJmb28iOiAiYmFyIn0sICJpYXQiOiAwfQ==.J3zdedMZSFNOimstjJat0V28rM_b1UU62XCp9dg_5kg=
```

#### The Header

For a general JWT object, the header can contain a variety of fields (e.g., describing the cryptographic operations applied to the token) depending on whether the JWT is a JWS or JWE. However, there are some fields which are common to both cases, and also the most commonly used: 

- **`alg`**: The algorithm used to sign the token, e.g. `HS256`, `HS384`, `HS512`. To see the list of supported algorithms in **flama**, have a look at it [here](https://github.com/vortico/flama/blob/7b79ae4b38efefc0fb02223a4a2fcb13837283af/flama/authentication/jwt/jws.py#L25).
- **`typ`**: The type parameter is used to declare the media type of the JWT. If present, it is recommended to have the value `JWT` to indicate that the object is a JWT. For more information on this field, see [RFC-7519 Sec. 5.1](https://datatracker.ietf.org/doc/html/rfc7519#section-5.1).
- **`cty`**: The content type is used to communicate structural information about the JWT. For example, if the JWT is a Nested JWT, the value of this field would be `JWT`. For more information on this field, see [RFC-7519 Sec. 5.2](https://datatracker.ietf.org/doc/html/rfc7519#section-5.2).

#### The Payload

The payload contains the claims (information) that the token is carrying. The claims are represented as a JSON object, and they can be divided into three categories, according to the standard [RFC-7519 Sec. 4](https://datatracker.ietf.org/doc/html/rfc7519#section-4):

- **Registered claims**: These are a set of predefined claims that are not mandatory but recommended. Some of the most common ones are `iss` (issuer), `sub` (subject), `aud` (audience), `exp` (expiration time), `nbf` (not before), `iat` (issued at), and `jti` (JWT ID). For a detailed explanation of each of these claims, see [RFC-7519 Sec. 4.1](https://datatracker.ietf.org/doc/html/rfc7519#section-4.1).
- **Public claims**: These are claims that are defined by the user and can be used to share information between different services.
- **Private claims**: These are claims that are defined by the user and are intended to be shared between the parties that are involved in the communication.


#### The Signature

The signature is used to ensure the integrity of the token and to verify that the sender of the token is who it claims to be. The signature is calculated using the header and the payload, and it is generated using the algorithm specified in the header. The signature is then appended to the token to create the final JWT.

## Implementing JWT Authentication with Flama

Having introduced the concept of JWT, its potential applications, besides a prototypical authentication flow, we can now move on to the implementation of a JWT-authenticated API using Flama. But, before we start, if you need to review the basics on how to create a simple API with **flama**, or how to run the API once you've already the code ready, then you might want to check out the [quick start guide](https://flama.dev/docs/getting-started/quickstart/). There, you'll find the fundamental concepts and steps required to follow this post. Now, without further ado, let's get started with the implementation.

### Setting up the development environment

Our first step is to create our development environment, and install all required dependencies for this project. The good thing is that for this example we only need to install **flama** to have all the necessary tools to implement JWT authentication. We'll be using [`poetry`](https://python-poetry.org/) to manage our dependencies, but you can also use `pip` if you prefer:

```bash
poetry add flama[full]
```

If you want to know how we typically organise our projects, have a look at our previous post [here](https://dev.to/vortico/introducing-flama-for-robust-machine-learning-apis-b3n#development-environment), where we explain in detail how to set up a python project with `poetry`, and the project folder structure we usually follow. 

### Base application

Let's start with a simple application that has a single public endpoint. This endpoint will return a brief description of the API.

```python
from flama import Flama

app = Flama(
    title="JWT protected API",
    version="1.0.0",
    description="JWT Authentication with Flama 🔥",
    docs="/docs/",
)

@app.get("/public/info/", name="public-info")
def info():
    """
    tags:
        - Public
    summary:
        Ping
    description:
        Returns a brief description of the API
    responses:
        200:
            description:
                Successful ping.
    """
    return {"title": app.schema.title, "description": app.schema.description, "public": True}
```

If you want to run this application, you can save the code above in a file called `main.py` under the `src` folder, and then run the following command (remember to have the `poetry` environment activated, otherwise you'll need to prefix the command with `poetry run`):

```bash
flama run --server-reload src.main:app

INFO:     Started server process [3267]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

where the `--server-reload` flag is optional and is used to reload the server automatically when the code changes. This is very useful during development, but you can remove it if you don't need it. For a full list of the available options, you can run `flama run --help`, or check the [documentation](https://flama.dev/docs/flama-cli/run/).

### Authentication: Flama JWT Component

Ok, now that we have our base application running, let's add a new endpoint that requires authentication. To do this, we'll need to use the following **flama** functionality:

- Components (specifically `JWTComponent`): They're the building blocks for dependency injection in **flama**.
- Middlewares (specifically `AuthenticationMiddleware`): They're used as a processing layer between the incoming requests from clients and the responses sent by the server.

Let's proceed and modify our base application to include the JWT authentication as intended, and then we'll explain the code in more detail.

```python
import uuid

from flama import Flama
from flama.authentication import AuthenticationMiddleware, JWTComponent
from flama.middleware import Middleware

JWT_SECRET_KEY = uuid.UUID(int=0).bytes  # The secret key used to signed the token
JWT_HEADER_KEY = "Authorization"  # Authorization header identifie
JWT_HEADER_PREFIX = "Bearer"  # Bearer prefix
JWT_ALGORITHM = "HS256"  # Algorithm used to sign the token
JWT_TOKEN_EXPIRATION = 300  # 5 minutes in seconds
JWT_REFRESH_EXPIRATION = 2592000  # 30 days in seconds
JWT_ACCESS_COOKIE_KEY = "access_token"
JWT_REFRESH_COOKIE_KEY = "refresh_token"

app = Flama(
    title="JWT-protected API",
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

# The same code as before here
# ...
```
Although we've decided to add the component and middleware after the initialisation of the `app`, you can also add them directly to the `Flama` constructor by passing the `components` and `middlewares` arguments:

```python
app = Flama(
    title="JWT-protected API",
    version="1.0.0",
    description="JWT Authentication with Flama 🔥",
    docs="/docs/",
    components=[
        JWTComponent(
            secret=JWT_SECRET_KEY,
            header_key=JWT_HEADER_KEY,
            header_prefix=JWT_HEADER_PREFIX,
            cookie_key=JWT_ACCESS_COOKIE_KEY,
        )
    ],
    middlewares=[
        Middleware(AuthenticationMiddleware),
    ]
)
```

This is just a matter of preference, and both ways are completely valid. 

With the modifications introduced above, we can proceed to add a new (and JWT protected) endpoint. However, before we do that, let's briefly explain in more detail the functionality we've just introduced, namely components and middlewares.

#### Flama Components

As you might've already noticed, whenever we create a new application we're instantiating a `Flama` object. As the application grows, as is the case right now, also grows the need to add more dependencies to it. Without [dependency injection](https://en.wikipedia.org/wiki/Dependency_injection) (DI), this would mean that the `Flama` class would have to create and manage all its dependencies internally. This would make the class tightly coupled to specific implementations and harder to test or modify. With DI the dependencies are provided to the class from the outside, which decouples the class from specific implementations, making it more flexible and easier to test. And, this is where components come into play in **flama**.

In **flama**, a Component is a building block for dependency injection. It encapsulates logic that determines how specific dependencies should be resolved when the application runs. Components can be thought of as self-contained units responsible for providing the necessary resources that the application's constituents need. Each Component in **flama** has a unique identity, making it easy to look up and inject the correct dependency during execution. Components are highly flexible, allowing you to handle various types of dependencies, whether they're simple data types, complex objects, or asynchronous operations. There are several built-in components in **flama**, although in this post we're going to exclusively focus on the `JWTComponent`, which (as all others) derives from the [`Component`](https://github.com/vortico/flama/blob/0ba81734bd56d74e728b9edfc2a8516bbf5e45ee/flama/injection/components.py#L12) class. 

The [`JWTComponent`](https://github.com/vortico/flama/blob/0ba81734bd56d74e728b9edfc2a8516bbf5e45ee/flama/authentication/components.py#L15) contains all the information and logic necessary for extracting a JWT from either the headers or cookies of an incoming request, decoding it, and then validating its authenticity. The component is initialised with the following parameters:

- `secret`: The secret key used to decode the JWT.
- `header_key`: The key used to identify the JWT in the request headers.
- `header_prefix`: The prefix used to identify the JWT in the request headers.
- `cookie_key`: The key used to identify the JWT in the request cookies.

In the code above, we've initialised the `JWTComponent` with some dummy values for the secret key, header key, header prefix, and cookie key. In a real-world scenario, you should replace these values with your own secret key and identifiers.


#### Flama Middlewares

Middleware is a crucial concept that acts as a processing layer between the incoming requests from clients and the responses sent by the server. In simpler terms, middleware functions as a gatekeeper or intermediary that can inspect, modify, or act on requests before they reach the core logic of your application, and also on the responses before they are sent back to the client.

In **flama**, middleware is used to handle various tasks that need to occur before a request is processed or after a response is generated. In this particular case, the task we want to handle is the authentication of incoming requests using JWT. To achieve this, we're going to use the built-in class [`AuthenticationMiddleware`](https://github.com/vortico/flama/blob/0ba81734bd56d74e728b9edfc2a8516bbf5e45ee/flama/authentication/middlewares.py#L20). This middleware is designed to ensure that only authorised users can access certain parts of your application. It works by intercepting incoming requests, checking for the necessary credentials (such as a valid JWT token), and then allowing or denying access based on the user's permissions which are encoded in the token.

Here’s how it works:

- Initialization: The middleware is initialized with the `Flama` application instance. This ties the middleware to your app, so it can interact with incoming requests and outgoing responses.
- Handling Requests: The `__call__` method of the middleware is called every time a request is made to your application. If the request type is http or websocket, the middleware checks if the route (the path the request is trying to access) requires any specific permissions.
- Permission Check: The middleware extracts the required permissions for the route from the route's tags. If no permissions are required, the request is passed on to the next layer of the application. If permissions are required, the middleware attempts to resolve a JWT token from the request. This is done using the previously discussed `JWTComponent`.
- Validating Permissions: Once the JWT token is resolved, the middleware checks the permissions associated with the token against those required by the route. If the user’s permissions match or exceed the required permissions, the request is allowed to proceed. Otherwise, the middleware returns a `403 Forbidden` response, indicating that the user does not have sufficient permissions.
- Handling Errors: If the JWT token is invalid or cannot be resolved, the middleware catches the exception and returns an appropriate error response, such as `401 Unauthorized`.

### Adding a protected endpoint

By now, we should have a pretty solid understanding on what our code does, and how it does it. Nevertheless, we still need to see what we have to do to add a protected endpoint to our application. Let's do it:

```python
@app.get("/private/info/", name="private-info", tags={"permissions": ["my-permission-name"]})
def protected_info():
    """
    tags:
        - Private
    summary:
        Ping
    description:
        Returns a brief description of the API
    responses:
        200:
            description:
                Successful ping.
    """
    return {"title": app.schema.title, "description": app.schema.description, "public": False}
```

And that's it! We've added a new endpoint that requires authentication to access. The functionality is exactly the same as the previous endpoint, but this time we've added the `tags` parameter to the `@app.get` decorator. The tag parameter can be used to specify additional metadata for an endpoint. But, if we use the special key `permissions` whilst using the `AuthenticationMiddleware`, we can specify the permissions required to access the endpoint. In this case, we've set the permissions to `["my-permission-name"]`, which means that only users with the permission `my-permission-name` will be able to access this endpoint. If a user tries to access the endpoint without the required permission, they will receive a `403 Forbidden` response.

### Running the application

If we put all the pieces together, we should have a fully functional application that has a public endpoint and a private endpoint that requires authentication. The full code should look something like this:

```python
import uuid

from flama import Flama
from flama.authentication import AuthenticationMiddleware, JWTComponent
from flama.middleware import Middleware

JWT_SECRET_KEY = uuid.UUID(int=0).bytes  # The secret key used to signed the token
JWT_HEADER_KEY = "Authorization"  # Authorization header identifie
JWT_HEADER_PREFIX = "Bearer"  # Bearer prefix
JWT_ALGORITHM = "HS256"  # Algorithm used to sign the token
JWT_TOKEN_EXPIRATION = 300  # 5 minutes in seconds
JWT_REFRESH_EXPIRATION = 2592000  # 30 days in seconds
JWT_ACCESS_COOKIE_KEY = "access_token"
JWT_REFRESH_COOKIE_KEY = "refresh_token"

app = Flama(
    title="JWT-protected API",
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
```

Running the application as before, we should see the following output:

```bash
flama run --server-reload src.main:app

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [48145] using WatchFiles
INFO:     Started server process [48149]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

If we navigate with our favourite browser to `http://127.0.0.1:8000/docs/` we should see the documentation of our API as shown below:

![Flama JWT Authentication](./.images/docs-no-auth.png)

As we can already expect, if we send a request to the public endpoint `/public/info/` we should receive a successful response:

```bash
curl --request GET \
  --url http://localhost:8000/public/info/ \
  --header 'Accept: application/json'
{"title":"JWT protected API","description":"JWT Authentication with Flama 🔥","public":true}
```

However, if we try to access the private endpoint `/private/info/` without providing a valid JWT token, we should receive a `401 Unauthorized` response:

```bash
curl --request GET \
  --url http://localhost:8000/private/info/ \
  --header 'Accept: application/json'
{"status_code":401,"detail":"Unauthorized","error":null}% 
```

Thus, we can say that the JWT authentication is working as expected, and only users with a valid JWT token will be able to access the private endpoint.

### Adding the login endpoint

As we've just seen, we have a private endpoint which requires a valid JWT token to be accessed. But, how do we get this token? The answer is simple: we need to create a login endpoint that will authenticate the user and return a valid JWT token. To do this, we're going to define the schemas for the input and output of the login endpoint (feel free to use your own schemas if you prefer, for instance, adding more fields to the input schema such as `username` or `email`):

```python
import uuid
import typing
import pydantic

class User(pydantic.BaseModel):
    id: uuid.UUID
    password: typing.Optional[str] = None


class UserToken(pydantic.BaseModel):
    id: uuid.UUID
    token: str
```

Now, let's add the login endpoint to our application:

```python
import http

from flama import types
from flama.authentication.jwt import JWT
from flama.http import APIResponse

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

    return APIResponse(
        status_code=http.HTTPStatus.OK, schema=types.Schema[UserToken], content={"id": str(user["id"]), "token": token}
    )
```

In this code snippet, we've defined a new endpoint `/auth/` that receives a `User` object as input and returns a `UserToken` object as output. The `User` object contains the `id` of the user and the `password` (which is optional for this example, since we're not going to be comparing it with any stored password). The `UserToken` object contains the `id` of the user and the generated `token` that will be used to authenticate the user in the private endpoints. The `token` is generated using the `JWT` class, and contains the permissions granted to the user, in this case, the permission `my-permission-name`, which will allow the user to access the private endpoint `/private/info/`. 

Now, let's test the login endpoint to see if it's working as expected. For this, we can proceed via the `/docs/` page:

![Flama JWT Authentication](./.images/docs-with-auth.png)

Or, we can use `curl` to send a request to the login endpoint:

```bash
curl --request POST \
  --url http://localhost:8000/auth/ \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --data '{
  "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
  "password": "string"
}'
```
which should return a response similar to this:

```bash
{"id":"497f6eca-6276-4993-bfeb-53cbbbba6f08","token":"eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJkYXRhIjogeyJpZCI6ICI0OTdmNmVjYS02Mjc2LTQ5OTMtYmZlYi01M2NiYmJiYTZmMDgiLCAicGVybWlzc2lvbnMiOiBbIm15LXBlcm1pc3Npb24tbmFtZSJdfSwgImlhdCI6IDE3MjU5ODk5NzQsICJpc3MiOiAidm9ydGljbyJ9.vwwgqahgtALckMAzQHWpNDNwhS8E4KAGwNiFcqEZ_04="}
```

That string is the JWT token that we can use to authenticate the user in the private endpoint. Let's try to access the private endpoint using the token:

```bash
curl --request GET \
  --url http://localhost:8000/private/info/ \
  --header 'Accept: application/json' \
  --header 'Authorization: Bearer eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJkYXRhIjogeyJpZCI6ICI0OTdmNmVjYS02Mjc2LTQ5OTMtYmZlYi01M2NiYmJiYTZmMDgiLCAicGVybWlzc2lvbnMiOiBbIm15LXBlcm1pc3Npb24tbmFtZSJdfSwgImlhdCI6IDE3MjU5ODk5NzQsICJpc3MiOiAidm9ydGljbyJ9.vwwgqahgtALckMAzQHWpNDNwhS8E4KAGwNiFcqEZ_04='
``` 

which now returns a successful response:

```bash
{"title":"JWT protected API","description":"JWT Authentication with Flama 🔥","public":false}
```

And that's it! We've successfully implemented JWT authentication in our `Flama` application. We now have a public endpoint that can be accessed without authentication, a private endpoint that requires a valid JWT token to be accessed, and a login endpoint that generates a valid JWT token for the user.

## Conclusions

The privatisation of some endpoints (even all at some instances) is a common requirement in many applications, even more so when dealing with sensitive data as is often the case in Machine Learning APIs which process personal or financial information, to name some examples. In this post, we've covered the fundamentals of token-based authentication for APIs, and how this can be implemented without much of a hassle using the new features introduced in the latest release of **flama** (introduced in a previous [post](https://dev.to/vortico/releasing-flama-17-3n78). Thanks to the `JWTComponent` and `AuthenticationMiddleware`, we can secure our API endpoints and control the access to them based on the permissions granted to the user, and all this with just a few modifications to our base __unprotected__ application. 

We hope you've found this post useful, and that you're now ready to implement JWT authentication in your own **flama** applications. If you have any questions or comments, feel free to reach out to us. We're always happy to help!

Stay tuned for more posts on **flama** and other exciting topics in the world of AI and software development. Until next time!

## About the authors

- [Vortico](https://vortico.tech/): We're specialised in software development to help businesses enhance and expand their AI and technology capabilities.
