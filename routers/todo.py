from fastapi import APIRouter, HTTPException, Depends, status, Response, Query
from motor.motor_asyncio import AsyncIOMotorCollection
from datetime import datetime, timezone
from typing import List, Optional

from schemas.todo import TaskCreate, TaskResponse, TaskUpdate
from services import get_next_pk, convert_id, get_tasks_collection


router = APIRouter(tags=["todo"])


@router.get("/", response_model=List[TaskResponse])
async def read_tasks(
    priority: Optional[str] = Query(None),
    complete: Optional[bool] = Query(None),
    collection: AsyncIOMotorCollection = Depends(get_tasks_collection),
):
    query = {}
    if complete is not None:
        query["is_finished"] = complete
    if priority:
        query["priority"] = priority  # type: ignore
    tasks = [convert_id(task) async for task in collection.find(query)]
    return tasks


@router.get("/{pk}", response_model=TaskResponse)
async def read_task(
    pk: int,
    priority: Optional[str] = Query(None),
    complete: Optional[bool] = Query(None),
    collection: AsyncIOMotorCollection = Depends(get_tasks_collection),
):
    query = {"pk": pk}
    if complete is not None:
        query["is_finished"] = complete
    if priority:
        query["priority"] = priority  # type: ignore

    task = await collection.find_one(query)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id {pk} not found")
    return convert_id(task)


@router.patch("/{pk}", response_model=TaskResponse)
async def update_task(
    pk: int,
    update_field: TaskUpdate,
    collection: AsyncIOMotorCollection = Depends(get_tasks_collection),
):
    update_data = update_field.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await collection.update_one({"pk": pk}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")

    updated_task = await collection.find_one({"pk": pk})
    return convert_id(updated_task)  # type: ignore


@router.delete("/{pk}")
async def delete_task(
    pk: int, collection: AsyncIOMotorCollection = Depends(get_tasks_collection)
):
    result = await collection.delete_one({"pk": pk})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Task with id {pk} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/add", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def add_task(
    task: TaskCreate, collection: AsyncIOMotorCollection = Depends(get_tasks_collection)
):
    next_pk = await get_next_pk(collection, "task_id")
    new_task_data = {
        "pk": next_pk,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "created_at": datetime.now(timezone.utc),
        "is_finished": False,
    }

    await collection.insert_one(new_task_data)
    return convert_id(new_task_data)
