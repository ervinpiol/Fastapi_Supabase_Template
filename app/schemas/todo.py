from pydantic import BaseModel
from typing import Optional

class TodoBase(BaseModel):
    title: str
    content: Optional[str] = None
    completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    completed: Optional[bool] = None

class TodoRead(TodoBase):
    id: int

    class Config:
        from_attributes = True
