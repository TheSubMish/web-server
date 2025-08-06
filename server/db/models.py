from database import Base
from sqlalchemy import Column, Integer
from typing import Any, List, Optional


class ModelManager:
    """
    ModelManager is a utility class for managing database models.
    Attributes:
        db_connection: The database connection object used to interact with the database.
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

    def __init__(self, db_connection: Any) -> None:
        self.db_connection: Any = db_connection

    def save(self, name: str, fields: Any) -> "Model":
        model = Model(name=name, fields=fields)
        session = self.db_connection.SessionLocal()
        model.save(session)
        return model

    def get(self, model_id: int) -> Optional["Model"]:
        session = self.db_connection.SessionLocal()
        model = session.query(Model).filter(Model.id == model_id).first()
        session.close()
        return model

    def update(self, model_id: int, **kwargs: Any) -> Optional["Model"]:
        session = self.db_connection.SessionLocal()
        model = session.query(Model).filter(Model.id == model_id).first()
        if model:
            for key, value in kwargs.items():
                setattr(model, key, value)
            model.save(session)
        return model

    def delete(self, model_id: int) -> bool:
        session = self.db_connection.SessionLocal()
        model = session.query(Model).filter(Model.id == model_id).first()
        if model:
            model.delete(session)
            return True
        return False

    def filter(self, **kwargs: Any) -> List["Model"]:
        session = self.db_connection.SessionLocal()
        query = session.query(Model)
        for key, value in kwargs.items():
            query = query.filter(getattr(Model, key) == value)
        results = query.all()
        session.close()
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

    objects: ModelManager

    name: str
    fields: Any

    def __init__(self, name: str, fields: Any) -> None:
        self.name = name
        self.fields = fields

    def __repr__(self) -> str:
        return f"Model(name={self.name}, fields={self.fields})"

    def __str__(self) -> str:
        return f"Model: {self.name} with fields"
