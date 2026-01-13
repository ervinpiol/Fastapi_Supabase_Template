from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoRead, TodoUpdate
from app.services.database import get_async_db

router = APIRouter(prefix="/todo", tags=["todo"])


@router.get("", response_model=List[TodoRead])
async def get_todos(
    session: AsyncSession = Depends(get_async_db),
    completed: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    offset = (page - 1) * limit

    query = select(Todo)
    if completed is not None:
        query = query.where(Todo.completed == completed)

    result = await session.execute(query.offset(offset).limit(limit))
    todos = result.scalars().all()
    return [TodoRead.model_validate(t) for t in todos]


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_async_db),
):
    todo = await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    return TodoRead.model_validate(todo)


@router.post("", response_model=TodoRead, status_code=201)
async def create_todo(
    todo_create: TodoCreate,
    session: AsyncSession = Depends(get_async_db),
):
    todo = Todo(**todo_create.model_dump(exclude_unset=True))

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    return TodoRead.model_validate(todo)


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate = Body(...),
    session: AsyncSession = Depends(get_async_db),
):
    todo = await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    for key, value in todo_update.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)

    await session.commit()
    await session.refresh(todo)

    return TodoRead.model_validate(todo)


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_async_db),
):
    todo = await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    await session.delete(todo)
    await session.commit()
