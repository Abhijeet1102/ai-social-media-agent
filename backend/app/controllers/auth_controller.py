from fastapi import APIRouter, Form, HTTPException

from app.auth import create_token, hash_password, verify_password
from app.database import users_collection

router = APIRouter()


@router.post("/signup")
def signup(username: str = Form(...), password: str = Form(...)):
    if len(password) > 72:
        raise HTTPException(status_code=400, detail="Password too long (max 72 chars)")

    existing_user = users_collection.find_one({"username": username})

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    users_collection.insert_one({
        "username": username,
        "password": hash_password(password),
    })

    return {"msg": "User created successfully"}


@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    user = users_collection.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Wrong password")

    token = create_token({"sub": username})

    return {
        "access_token": token,
        "token_type": "bearer",
    }
