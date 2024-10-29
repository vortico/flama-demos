from flama import Flama
from flama.ddd import WorkerComponent
from flama.sqlalchemy import SQLAlchemyModule

from src import resources, worker

DATABASE_URL = "sqlite+aiosqlite:///models.db"

app = Flama(
    title="Domain-driven API",
    version="1.0.0",
    description="Domain-driven design with Flama 🔥",
    docs="/docs/",
    modules=[SQLAlchemyModule(DATABASE_URL)],
    components=[WorkerComponent(worker=worker.RegisterWorker())],
)


# app.resources.add_resource("/admin/", resources.AdminResource)
app.resources.add_resource("/user/", resources.UserResource)


@app.get("/", name="info")
def info():
    """
    tags:
        - Info
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
