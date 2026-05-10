import os

from fastapi import APIRouter, Depends, HTTPException

from app.auth import verify_token
from app.database import posts_collection, users_collection

router = APIRouter()


@router.get("/")
def home():
    return {"message": "Backend is running "}


@router.get("/testdb")
def test_db():
    posts_collection.insert_one({"test": "working"})
    return {"msg": "inserted"}


@router.delete("/reset-users")
def reset_users(user=Depends(verify_token)):
    if user["sub"] != os.getenv("ADMIN_USERNAME"):
        raise HTTPException(status_code=403, detail="Admin access required")

    users_collection.delete_many({})
    return {"msg": "All users deleted"}
