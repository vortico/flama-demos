import logging

from sqlalchemy import create_engine

from src.models import metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Set up the SQLite database
    engine = create_engine("sqlite:///models.db", echo=False)

    # Create the database tables
    metadata.create_all(engine)

    # Prints a success message
    print("Database and User table created successfully.")
