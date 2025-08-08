from server.db.models import Model
from sqlalchemy import Column, String


class ContactModel(Model):

    __tablename__ = "contacts"

    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    message = Column(String, nullable=False)
