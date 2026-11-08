import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from fastapi.security import( OAuth2PasswordBearer, OAuth2PasswordRequestForm,
)
from pydantic import BaseModel, Field

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing. Add it to your .env file."
    )

app = FastAPI(title="AI Dashboard Task  API")
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"
    "http://localhost:8501"],
    allow_credentials=False, allow_methods=["GET", "POST", "PATCH"], 
    allow_headers=["Authorization", "Content-Type"],
)

#Demo credentials only - not production authentication.
USERS = {
    "admin": "password123",
    "student": "learn2026",
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

tasks = [
    {
        "id": 1,
        "title": "Complete Module 5",
        "done": True,
        "user": "admin",
    },
    {
        "id": 2,
        "title": "Start Module 6",
        "done": True,
        "user": "admin",
    },
    {
        "id": 3,
        "title": "Build Streamlit app",
        "done": False,
        "user": "admin",
    }
]

next_id = 4

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

#Create a signed JWT for the logged-in user.
def create_access_token(username):

    now = datetime.now(timezone.utc)

    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    }

    return jwt.encode(
        payload, 
        SECRET_KEY, 
        algorithm=ALGORITHM
    )

#Verifty the JWT and return its username
def get_current_user(token: str = Depends(oauth2_scheme)):

    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"require": ["sub", "exp", "iat"]},
        )

        username = payload.get("sub")

        if not isinstance(username, str) or username not in USERS:
            raise HTTPException(
                status_code=401, 
                detail="Invalid token",
            )
        return username
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expiredtoken",
        )

@app.post("/auth/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username

    if USERS.get(username) != form_data.password:
        raise HTTPException(
            status_code=401, 
            detail="Invalid credentials",
        )
    
    token = create_access_token(username)
    return {
        "access_token": token, 
        "token_type": "bearer"
    }

@app.get("/tasks")
def get_tasks(user: str = Depends(get_current_user)):
    return [
        task for task in tasks 
        if task["user"] == user
    ]

@app.post("/tasks", status_code=201)
def create_task(
    task: TaskCreate, 
    user: str = Depends(get_current_user),
):
    global next_id

    title = task.title.strip()

    if not title:
        raise HTTPException(
            status_code=422, 
            detail="Task title cannot be empty",
        )
    new_task = {
        "id": next_id, 
        "title": title, 
        "done": False, 
        "user": user
    }

    tasks.append(new_task)
    next_id += 1

    return new_task

@app.patch("/tasks/{task_id}")
def toggle_task(
    task_id: int, 
    user: str = Depends(get_current_user),
):
    for task in tasks:
        if task["id"] == task_id and task["user"] == user:
            task["done"] = not task["done"]
            return task
        
    raise HTTPException(
        status_code=404, 
        detail="Task not found",
    )

@app.get("/stats")
def get_stats(user: str = Depends(get_current_user)):
    user_tasks = [
        task for task in tasks 
        if task["user"] == user
    ]
    total = len(user_tasks)
    done = sum(task["done"] for task in user_tasks)

    return {
        "total": total, 
        "done": done, 
        "pending": total - done,
    }

# Simple in-memory auth (for demo only — not production!)
USERS = {"admin": "password123", "student": "learn2026"}
tokens = {}  # token -> username mapping
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# In-memory tasks
tasks = [
    {"id": 1, "title": "Complete Module 5", "done": True, "user": "admin"},
    {"id": 2, "title": "Start Module 6", "done": True, "user": "admin"},
    {"id": 3, "title": "Build Streamlit app", "done": False, "user": "admin"},
]
next_id = 4

class TaskCreate(BaseModel):
    title: str

def get_current_user(token: str = Depends(oauth2_scheme)):
    username = tokens.get(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username

@app.post("/auth/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if USERS.get(form_data.username) != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = secrets.token_hex(32)
    tokens[token] = form_data.username
    return {"access_token": token, "token_type": "bearer"}

@app.get("/tasks")
def get_tasks(user: str = Depends(get_current_user)):
    return [t for t in tasks if t["user"] == user]

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate, user: str = Depends(get_current_user)):
    global next_id
    new_task = {"id": next_id, "title": task.title, "done": False, "user": user}
    tasks.append(new_task)
    next_id += 1
    return new_task

@app.patch("/tasks/{task_id}")
def toggle_task(task_id: int, user: str = Depends(get_current_user)):
    for task in tasks:
        if task["id"] == task_id and task["user"] == user:
            task["done"] = not task["done"]
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/stats")
def get_stats(user: str = Depends(get_current_user)):
    user_tasks = [t for t in tasks if t["user"] == user]
    total = len(user_tasks)
    done = sum(1 for t in user_tasks if t["done"])
    return {"total": total, "done": done, "pending": total - done}