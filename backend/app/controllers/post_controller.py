from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI

from app.auth import verify_token
from app.config import OPENAI_API_KEY
from app.database import connected_accounts_collection, posts_collection, scheduled_collection
from app.services.linkedin_service import publish_text_post

router = APIRouter()

if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY missing")

client_ai = OpenAI(api_key=OPENAI_API_KEY)


@router.get("/generate")
def generate(topic: str, user=Depends(verify_token)):
    try:
        prompt = f"Generate a catchy Instagram caption and 5 hashtags for: {topic}"

        response = client_ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        result = response.choices[0].message.content

        posts_collection.insert_one({
            "topic": topic,
            "result": result,
            "user": user["sub"],
            "created_at": datetime.utcnow(),
        })

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/posts")
def get_posts(user=Depends(verify_token)):
    try:
        return list(posts_collection.find({"user": user["sub"]}, {"_id": 0}))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/schedule")
def schedule_post(data: dict, user=Depends(verify_token)):
    try:
        platforms = data.get("platforms", ["linkedin"])

        if "linkedin" in platforms:
            linkedin_account = connected_accounts_collection.find_one({
                "user": user["sub"],
                "platform": "linkedin",
                "status": "connected",
            })
            if not linkedin_account:
                raise HTTPException(status_code=400, detail="Connect LinkedIn before scheduling.")

        scheduled_collection.insert_one({
            "content": data["content"],
            "date": data["date"],
            "time": data["time"],
            "platforms": platforms,
            "status": "pending",
            "user": user["sub"],
            "created_at": datetime.utcnow(),
        })

        return {"msg": "Post successfully scheduled"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/post-now/linkedin")
def post_now_linkedin(data: dict, user=Depends(verify_token)):
    content = data.get("content")

    if not content:
        raise HTTPException(status_code=400, detail="Content is required")

    account = connected_accounts_collection.find_one({
        "user": user["sub"],
        "platform": "linkedin",
        "status": "connected",
    })

    if not account:
        raise HTTPException(status_code=400, detail="Connect LinkedIn before posting.")

    linkedin_post_id = publish_text_post(account, content)

    now = datetime.utcnow()
    scheduled_collection.insert_one({
        "content": content,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "platforms": ["linkedin"],
        "status": "posted",
        "user": user["sub"],
        "created_at": now,
        "posted_at": now,
        "platform_results": {
            "linkedin": linkedin_post_id,
        },
        "post_type": "instant",
    })

    return {
        "msg": "Post successful",
        "linkedin_post_id": linkedin_post_id,
    }


@router.get("/scheduled")
def get_scheduled(user=Depends(verify_token)):
    try:
        return list(
            scheduled_collection.find(
                {"user": user["sub"]},
                {"_id": 0},
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
