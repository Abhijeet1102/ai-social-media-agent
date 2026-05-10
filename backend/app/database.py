from pymongo import MongoClient
from app.config import DATABASE_NAME, MONGO_URI

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]

scheduled_collection = db["scheduled_posts"]
posts_collection = db["posts"]
users_collection = db["users"]
connected_accounts_collection = db["connected_accounts"]
oauth_states_collection = db["oauth_states"]
logs_collection = db["logs"]
