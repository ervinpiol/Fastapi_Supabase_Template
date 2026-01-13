from sqlalchemy import Column, String, Boolean, Integer
from app.services.database import Base

class Todo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=True)
    completed = Column(Boolean, default=False)