from pymongo import MongoClient
from datetime import datetime, UTC
import time

print(" FILE STARTED")

# MongoDB
client = MongoClient("mongodb+srv://social_user:apnacollege@cluster0.dskqtu.mongodb.net/?appName=Cluster0")
db = client["social_media"]

scheduled_collection = db["scheduled_posts"]
logs_collection = db["logs"]

def run_worker():
    print(" Worker started...")

    while True:
        now = datetime.now(UTC)

        posts = scheduled_collection.find({"status": "pending"})

        for post in posts:
            try:
                scheduled_time = datetime.strptime(
                    post["date"] + " " + post["time"],
                    "%Y-%m-%d %H:%M"
                ).replace(tzinfo=UTC)

                #  check time (±30 sec window)
                if abs((scheduled_time - now).total_seconds()) <= 30:

                    print(" Posting:", post["content"])

                    #  SUCCESS UPDATE
                    scheduled_collection.update_one(
                        {"_id": post["_id"]},
                        {"$set": {
                            "status": "posted",
                            "posted_at": datetime.now(UTC)
                        }}
                    )

                    #  LOG SUCCESS
                    logs_collection.insert_one({
                        "action": "post_success",
                        "content": post["content"],
                        "time": datetime.now(UTC)
                    })

            except Exception as e:
                print(" Error:", str(e))

                #  Retry logic
                retry_count = post.get("retry", 0)

                if retry_count < 3:
                    scheduled_collection.update_one(
                        {"_id": post["_id"]},
                        {"$inc": {"retry": 1}}
                    )
                else:
                    scheduled_collection.update_one(
                        {"_id": post["_id"]},
                        {"$set": {
                            "status": "failed",
                            "error": str(e)
                        }}
                    )

                #  LOG FAILURE
                logs_collection.insert_one({
                    "action": "post_failed",
                    "error": str(e),
                    "time": datetime.now(UTC)
                })

        time.sleep(10)  #  every 10 sec


if __name__ == "__main__":
    run_worker()