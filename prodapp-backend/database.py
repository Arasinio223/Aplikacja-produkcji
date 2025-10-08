from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# dane do logowania – dopasuj do swojej konfiguracji PostgreSQL
DB_USER = "prodapp"
DB_PASS = "prodapp123"
DB_HOST = "localhost"
DB_NAME = "prodapp"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# tworzymy silnik i sesję
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# baza klas modeli
Base = declarative_base()
