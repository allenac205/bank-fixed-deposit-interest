import os
from dotenv import load_dotenv

from pydantic import BaseModel
from pydantic_settings import BaseSettings


load_dotenv()


class DbTables(BaseModel):
    USER_TABLE: str = os.getenv("USER_TABLE")
    INTREST_TABLE: str = os.getenv("INTREST_TABLE")
    DEPOSITS_TABLE: str = os.getenv("DEPOSITS_TABLE")
    STATEMENT_RANGES_TABLE: str = os.getenv("STATEMENT_RANGES_TABLE")


class Settings(BaseSettings):
    db_tables: DbTables = DbTables()


settings = Settings()