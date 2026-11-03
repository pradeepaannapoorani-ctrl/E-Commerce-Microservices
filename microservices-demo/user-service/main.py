from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="User Service", version="1.0.0")

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr

class User(UserCreate):
    id: int

users = [
    User(id=1, name="Alice", email="alice@example.com"),
    User(id=2, name="Bob", email="bob@example.com"),
]

@app.get("/health")
def health():
    return {"status": "healthy", "service": "user-service"}

@app.get("/users", response_model=list[User])
def get_users():
    return users

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    if any(user.email == payload.email for user in users):
        raise HTTPException(status_code=409, detail="Email already exists")
    new_user = User(id=max((u.id for u in users), default=0) + 1, **payload.model_dump())
    users.append(new_user)
    return new_user
