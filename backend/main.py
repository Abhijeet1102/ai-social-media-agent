from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from openai import OpenAI
from pymongo import MongoClient
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

print(" APP STARTING...")

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise Exception("OPENAI_API_KEY missing")

client_ai = OpenAI(api_key=api_key)

# MongoDB
mongo_client = MongoClient("mongodb+srv://social_user:apnacollege@cluster0.dskqtu.mongodb.net/?appName=Cluster0")
db = mongo_client["social_media"]

scheduled_collection = db["scheduled_posts"]
posts_collection = db["posts"]
users_collection = db["users"]

#  AUTH CONFIG
SECRET_KEY = os.getenv("SECRET_KEY", "fallbacksecret")  # better than hardcoded
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#  HELPERS

def verify_password(plain, hashed):
    plain = plain[:72]  #  bcrypt fix
    return pwd_context.verify(plain, hashed)

def hash_password(password):
    password = password[:72]  #  bcrypt fix
    return pwd_context.hash(password)

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

#  HOME
@app.get("/")
def home():
    return {"message": "Backend is running "}

#  SIGNUP
@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...)):

    if len(password) > 72:
        raise HTTPException(status_code=400, detail="Password too long (max 72 chars)")

    existing_user = users_collection.find_one({"username": username})

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    users_collection.insert_one({
        "username": username,
        "password": hash_password(password)
    })

    return {"msg": "User created successfully"}

#  LOGIN
@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):

    user = users_collection.find_one({"username": username})

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Wrong password")

    token = create_token({"sub": username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

#  GENERATE (Protected)
@app.get("/generate")
def generate(topic: str, user=Depends(verify_token)):
    try:
        prompt = f"Generate a catchy Instagram caption and 5 hashtags for: {topic}"

        response = client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content

        posts_collection.insert_one({
            "topic": topic,
            "result": result,
            "user": user["sub"],
            "created_at": datetime.utcnow()
        })

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#  GET POSTS
@app.get("/posts")
def get_posts(user=Depends(verify_token)):
    try:
        posts = list(posts_collection.find({"user": user["sub"]}, {"_id": 0}))
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#  SCHEDULE POST
@app.post("/schedule")
def schedule_post(data: dict, user=Depends(verify_token)):
    try:
        scheduled_collection.insert_one({
            "content": data["content"],
            "date": data["date"],
            "time": data["time"],
            "status": "pending",
            "user": user["sub"],
            "created_at": datetime.utcnow()
        })

        return {"msg": "Post scheduled successfully "}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#  GET SCHEDULED POSTS
@app.get("/scheduled")
def get_scheduled(user=Depends(verify_token)):
    try:
        posts = list(
            scheduled_collection.find(
                {"user": user["sub"]},
                {"_id": 0}
            )
        )
        return posts

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#  TEST DB
@app.get("/testdb")
def test_db():
    posts_collection.insert_one({"test": "working"})
    return {"msg": "inserted"}

    @app.get("/reset-users")
def reset_users():
    users_collection.delete_many({})
    return {"msg": "All users deleted"}