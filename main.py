from fastapi import FastAPI, HTTPException, Path, Query, status, Depends
from pydantic import BaseModel, Field 
from typing import Optional, Dict 

app = FastAPI(
    title = "Pure FastAPI task Manager",
    description = "A small project designed to explore core FastAPI features straight from the docs.",
    version = "1.0.0"
)

class Task(BaseModel):
    title: str = Field(..., min_length=3, max_length=50, examples=["Finish presentation"])
    description: Optional[str] = Field(None, max_length=200, examples=["Prepare the quartly slides."])
    completed: bool = Field(default=False)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length = 200)
    completed: Optional[bool] = None 

DB: Dict[int, dict] = {
    1: {"title": "Learn FastAPI Docs", "description": "Read advanced security section", "completed": False},
    1: {"title": "Build a mini-app", "description": "Keep it pure FastAPI without extra databases", "completed": True},
}

def common_api_maker():
    return "[API-LOG]"

@app.get("/tasks", status_code=status.HTTP_200_OK, tags=["tasks"])
def get_tasks(
    completed:Optional[bool] = Query(None, description="Filter tasks by completion status"),
    logger: str = Depends(common_api_maker)
):
    print(f"{logger} Fetching tasks list...")
    if completed is not None:
        return {k: v for k, v in DB.items() if v["completed"] == completed}
    return DB 

@app.post("/tasks", status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(task: Task):
    # increase value in dummy DB
    new_id = max(DB.keys(), default=0) + 1 
    DB[new_id] = task.model_dump()
    return {"id": new_id, **DB[new_id]}

@app.put("/tasks/{task_id}", status_code=status.HTTP_200_OK, tags=["Tasks"])
def update_task(task_id: int, task_data: TaskUpdate):
    if task_id not in DB:
        raise HTTPException(status_code=404, details="Task not found.")
    stored_data = DB[task_id]
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        stored_data[key] = value
    DB[task_id] = stored_data 
    return {"id": task_id, **stored_data}

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task(task_id: int):
    if task_id not in DB:
        raise HTTPException(status_code= 404, details= "Task not found.")
    del DB[task_id]
    return 