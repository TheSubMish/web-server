from contextlib import contextmanager
from database import Base, database, DatabaseConnection
from sqlalchemy import Column, Integer
from typing import Any, List, Optional


class ModelManager:
    """
    ModelManager is a utility class for managing database models.
    Attributes:
        database: The database connection object used to interact with the database.
    Methods:
        save(name, fields):
            Creates and saves a new model instance with the specified name and fields.
        get(model_id):
            Retrieves a model instance by its unique identifier.
        update(model_id, **kwargs):
            Updates the fields of an existing model instance identified by model_id.
        delete(model_id):
            Deletes the model instance with the specified model_id from the database.
        filter(**kwargs):
            Retrieves a list of model instances that match the given filter criteria.
    """

    def __init__(self) -> None:
        self.database: DatabaseConnection = database

    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.database.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def save(self, id: int, fields: Any) -> "Model":

        model = Model(id=id, **fields)
        with self.get_session() as session:
            session.add(model)
            session.commit()
        return model

    def create(self, fields: Any) -> "Model":
        """Create a new model instance using SQLAlchemy and save it to the database"""
        model = Model(**fields)
        with self.get_session() as session:
            session.add(model)
            session.commit()
            session.refresh(model)
        return model

    def get(self, model_id: int) -> Optional["Model"]:
        with self.get_session() as session:
            model = session.query(Model).filter_by(id=model_id).first()
            return model

    def update(self, model_id: int, **kwargs: Any) -> Optional["Model"]:
        with self.get_session() as session:
            model = session.query(Model).filter_by(id=model_id).first()
            if model:
                for key, value in kwargs.items():
                    setattr(model, key, value)
                session.add(model)
                session.commit()
            return model

    def delete(self, model_id: int) -> bool:
        with self.get_session() as session:
            model = session.query(Model).filter_by(id=model_id).first()
            if model:
                session.delete(model)
                return True
            return False

    def filter(self, **kwargs: Any) -> List["Model"]:
        with self.get_session() as session:
            query = session.query(Model)
            for key, value in kwargs.items():
                query = query.filter(getattr(Model, key) == value)
            results = query.all()
            for result in results:
                session.expunge(result)
            return results

    def all(self) -> List["Model"]:
        """Retrieve all model instances"""
        with self.get_session() as session:
            results = session.query(Model).all()
            for result in results:
                session.expunge(result)
            return results


class Model(Base):
    """
    Abstract base class for database models.

    Attributes:
        id (int): Primary key for the model, indexed.
        objects (ModelManager): Manager for model queries and operations.
        name (str): Name of the model instance.
        fields (Any): Fields associated with the model instance.

    Methods:
        __init__(name, fields): Initializes the model with a name and fields.
        __repr__(): Returns a string representation of the model instance.
        __str__(): Returns a human-readable string for the model instance.
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    def __init__(self, id: int, fields: Any) -> None:
        super().__init__()
        self.id = id
        self.fields = fields

    def __repr__(self) -> str:
        return f"Model(id={self.id}, fields={self.fields})"

    def __str__(self) -> str:
        return f"Model: {self.id} with fields"

    objects = ModelManager()
