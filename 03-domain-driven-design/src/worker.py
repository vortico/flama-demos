from flama.ddd import SQLAlchemyWorker

from src import repositories

__all__ = ["RegisterWorker"]


class RegisterWorker(SQLAlchemyWorker):
    user: repositories.UserRepository
