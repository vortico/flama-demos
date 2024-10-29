import uuid

import sqlalchemy
from flama.sqlalchemy import metadata
from sqlalchemy.dialects.postgresql import UUID

__all__ = ["user_table", "metadata"]

user_table = sqlalchemy.Table(
    "user",
    metadata,
    sqlalchemy.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4),
    sqlalchemy.Column("name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("surname", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("email", sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("active", sqlalchemy.Boolean, nullable=False),
)
