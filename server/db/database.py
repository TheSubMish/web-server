import sqlite3
import os

from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class DatabaseConnection:
    """
    DatabaseConnection manages database connectivity for the application.
    Attributes:
        use_sqlite (bool): Indicates whether SQLite should be used as the database backend.
    Methods:
        __init__():
            Initializes the DatabaseConnection instance and determines the database backend.
        _check_db():
            Checks the configuration to decide if SQLite should be used.
        _create_sqlite_connection(db_file):
            Creates and returns a SQLite connection to the specified database file.
        get_connection():
            Returns a database connection based on the selected backend. Currently, only SQLite is supported.
    """

    def __init__(self) -> None:
        self.db_file: str = "default.db"
        self.use_sqlite: bool = self._check_db()
        self.engine: Optional[Engine] = None
        self.SessionLocal = None

        if self.use_sqlite:
            self.engine = self._create_sqlalchemy_engine(self.db_file)
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

    def _check_db(self) -> bool:

        try:
            import main
        except ImportError as e:
            main = None

        if main is not None and hasattr(main, "USE_SQLITE"):
            use_sqlite: bool = main.USE_SQLITE
        else:
            use_sqlite = False
        return use_sqlite

    def _create_sqlite_connection(self, db_file: str) -> sqlite3.Connection | None:
        if not os.path.exists(db_file):
            open(db_file, "w").close()

        conn: sqlite3.Connection | None = None
        try:
            conn = sqlite3.connect(db_file)
            print("Connection established")
        except sqlite3.Error as e:
            print(e)
        return conn

    def _create_sqlalchemy_engine(self, db_file: str) -> Engine:
        if not os.path.exists(db_file):
            open(db_file, "w").close()

        db_url = f"sqlite:///{db_file}"

        engine = create_engine(
            db_url, connect_args={"check_same_thread": False}, echo=False
        )
        return engine

    def get_connection(self) -> sqlite3.Connection:
        if self.use_sqlite:
            conn = self._create_sqlite_connection("default.db")
            if conn is None:
                raise sqlite3.Error("Failed to create SQLite connection.")
            return conn
        else:
            raise NotImplementedError("Only SQLite is currently supported.")

    def get_engine(self) -> Engine:
        """Get SQLAlchemy engine"""
        if not self.use_sqlite:
            raise NotImplementedError("Only SQLite is currently supported.")

        if self.engine is None:
            raise RuntimeError("SQLAlchemy engine not initialized.")

        return self.engine

    def get_session(self) -> Session:
        """Get a new SQLAlchemy session"""
        if not self.use_sqlite:
            raise NotImplementedError("Only SQLite is currently supported.")

        if self.SessionLocal is None:
            raise RuntimeError("SQLAlchemy session factory not initialized.")

        return self.SessionLocal()

    def get_session_factory(self):
        """Get the session factory for dependency injection"""
        return self.SessionLocal


database = DatabaseConnection()
db_connection = database.get_connection()
