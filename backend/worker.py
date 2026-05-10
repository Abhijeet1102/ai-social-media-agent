from datetime import UTC, datetime
import time

from fastapi import HTTPException

from app.database import connected_accounts_collection, logs_collection, scheduled_collection
from app.services.linkedin_service import publish_text_post

print(" FILE STARTED")


def mark_failed(post, error):
    retry_count = post.get("retry", 0)

    if retry_count < 3:
        scheduled_collection.update_one(
            {"_id": post["_id"]},
            {"$inc": {"retry": 1}, "$set": {"last_error": error}},
        )
    else:
        scheduled_collection.update_one(
            {"_id": post["_id"]},
            {
                "$set": {
                    "status": "failed",
                    "error": error,
                    "failed_at": datetime.now(UTC),
                }
            },
        )

    logs_collection.insert_one({
        "action": "post_failed",
        "post_id": post["_id"],
        "error": error,
        "time": datetime.now(UTC),
    })


def publish_linkedin(post):
    account = connected_accounts_collection.find_one({
        "user": post["user"],
        "platform": "linkedin",
        "status": "connected",
    })

    if not account:
        raise HTTPException(status_code=400, detail="LinkedIn account is not connected.")

    linkedin_post_id = publish_text_post(account, post["content"])
    return linkedin_post_id


def publish_due_post(post):
    platforms = post.get("platforms", [])
    results = {}

    if "linkedin" in platforms:
        results["linkedin"] = publish_linkedin(post)

    if not platforms:
        results["simulation"] = "No platform selected"

    scheduled_collection.update_one(
        {"_id": post["_id"]},
        {
            "$set": {
                "status": "posted",
                "posted_at": datetime.now(UTC),
                "platform_results": results,
            }
        },
    )

    logs_collection.insert_one({
        "action": "post_success",
        "post_id": post["_id"],
        "content": post["content"],
        "platform_results": results,
        "time": datetime.now(UTC),
    })


def run_worker():
    print(" Worker started...")

    while True:
        now = datetime.now(UTC)
        posts = scheduled_collection.find({"status": "pending"})

        for post in posts:
            try:
                scheduled_time = datetime.strptime(
                    post["date"] + " " + post["time"],
                    "%Y-%m-%d %H:%M",
                ).replace(tzinfo=UTC)

                if abs((scheduled_time - now).total_seconds()) <= 30:
                    print(" Posting:", post["content"])
                    publish_due_post(post)

            except Exception as e:
                print(" Error:", str(e))
                mark_failed(post, str(e))

        time.sleep(10)


if __name__ == "__main__":
    run_worker()
