from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import models
import crud
from database import engine, get_db
from schemas import TaskCreate, TaskUpdate, TaskListResponse, TaskResponse

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow Pro API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic 검증 오류를 400으로 통일한다 (스펙: 02-specs.md)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )


@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, payload)


@app.get("/api/tasks", response_model=list[TaskListResponse])
def list_tasks(db: Session = Depends(get_db)):
    return crud.get_tasks(db)


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return crud.get_task(db, task_id)


@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    return crud.update_task(db, task_id, payload)


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    crud.delete_task(db, task_id)
