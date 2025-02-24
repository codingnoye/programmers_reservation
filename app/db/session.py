import os
from dotenv import load_dotenv

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from typing import Annotated

load_dotenv()
USERNAME = os.getenv("POSTGRES_USERNAME")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
HOST = os.getenv("POSTGRES_HOST")
PORT = os.getenv("POSTGRES_PORT")
DB = os.getenv("POSTGRES_DB")

# PostgreSQL
engine = create_engine(f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}')

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session())]