from flama.ddd import SQLAlchemyTableRepository
from sqlalchemy import func

from src import models

__all__ = ["UserRepository"]


class UserRepository(SQLAlchemyTableRepository):
    _table = models.user_table

    async def count_active_users(self):
        return len((await self._connection.execute(self._table.select().where(self._table.c.active == True))).all())
