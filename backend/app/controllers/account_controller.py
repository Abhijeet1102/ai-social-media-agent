import secrets
from datetime import datetime
from urllib.parse import urlencode

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from app.auth import verify_token
from app.config import FRONTEND_URL
from app.database import connected_accounts_collection, oauth_states_collection
from app.services.linkedin_service import (
    build_authorization_url,
    exchange_code_for_token,
    save_linkedin_account,
)
from app.services.instagram_service import (
    build_authorization_url as build_instagram_authorization_url,
    exchange_code_for_token as exchange_instagram_code_for_token,
    save_instagram_account,
)
from app.services.facebook_service import (
    build_authorization_url as build_facebook_authorization_url,
    exchange_code_for_token as exchange_facebook_code_for_token,
    save_facebook_account,
)
from app.services.youtube_service import (
    build_authorization_url as build_youtube_authorization_url,
    exchange_code_for_token as exchange_youtube_code_for_token,
    save_youtube_account,
)

router = APIRouter()


def frontend_redirect(platform: str, status: str, message: str):
    query = urlencode({
        "connect": platform,
        "status": status,
        "message": message,
    })
    return RedirectResponse(f"{FRONTEND_URL}/?{query}")


@router.get("/connected-accounts")
def get_connected_accounts(user=Depends(verify_token)):
    return list(
        connected_accounts_collection.find(
            {"user": user["sub"]},
            {
                "_id": 0,
                "access_token": 0,
                "refresh_token": 0,
                "id_token": 0,
                "token_type": 0,
            },
        )
    )


@router.delete("/connected-accounts/{platform}")
def disconnect_account(platform: str, user=Depends(verify_token)):
    result = connected_accounts_collection.delete_one({
        "user": user["sub"],
        "platform": platform,
    })

    if result.deleted_count == 0:
        return {"msg": f"{platform} was not connected"}

    return {"msg": f"{platform} disconnected"}


@router.get("/auth/linkedin/start")
def start_linkedin_auth(user=Depends(verify_token)):
    state = secrets.token_urlsafe(32)
    oauth_states_collection.insert_one({
        "state": state,
        "platform": "linkedin",
        "user": user["sub"],
        "created_at": datetime.utcnow(),
    })

    return {"url": build_authorization_url(state)}


@router.get("/auth/linkedin/callback")
def linkedin_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    error_description: str = None,
):
    if error:
        return frontend_redirect("linkedin", "error", error_description or error)

    if not code or not state:
        return frontend_redirect("linkedin", "error", "Missing LinkedIn callback data")

    state_record = oauth_states_collection.find_one({
        "state": state,
        "platform": "linkedin",
    })

    if not state_record:
        return frontend_redirect("linkedin", "error", "Invalid LinkedIn state")

    try:
        token_data = exchange_code_for_token(code)
        save_linkedin_account(state_record["user"], token_data)
    except Exception as e:
        return frontend_redirect("linkedin", "error", str(e))

    oauth_states_collection.delete_one({"_id": state_record["_id"]})
    return frontend_redirect("linkedin", "success", "LinkedIn connected")


@router.get("/auth/youtube/start")
def start_youtube_auth(user=Depends(verify_token)):
    state = secrets.token_urlsafe(32)
    oauth_states_collection.insert_one({
        "state": state,
        "platform": "youtube",
        "user": user["sub"],
        "created_at": datetime.utcnow(),
    })

    return {"url": build_youtube_authorization_url(state)}


@router.get("/auth/youtube/callback")
def youtube_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    error_description: str = None,
):
    if error:
        return frontend_redirect("youtube", "error", error_description or error)

    if not code or not state:
        return frontend_redirect("youtube", "error", "Missing YouTube callback data")

    state_record = oauth_states_collection.find_one({
        "state": state,
        "platform": "youtube",
    })

    if not state_record:
        return frontend_redirect("youtube", "error", "Invalid YouTube state")

    try:
        token_data = exchange_youtube_code_for_token(code)
        save_youtube_account(state_record["user"], token_data)
    except Exception as e:
        return frontend_redirect("youtube", "error", str(e))

    oauth_states_collection.delete_one({"_id": state_record["_id"]})
    return frontend_redirect("youtube", "success", "YouTube connected")


@router.get("/auth/instagram/start")
def start_instagram_auth(user=Depends(verify_token)):
    state = secrets.token_urlsafe(32)
    oauth_states_collection.insert_one({
        "state": state,
        "platform": "instagram",
        "user": user["sub"],
        "created_at": datetime.utcnow(),
    })

    return {"url": build_instagram_authorization_url(state)}


@router.get("/auth/instagram/callback")
def instagram_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    error_description: str = None,
):
    if error:
        return frontend_redirect("instagram", "error", error_description or error)

    if not code or not state:
        return frontend_redirect("instagram", "error", "Missing Instagram callback data")

    state_record = oauth_states_collection.find_one({
        "state": state,
        "platform": "instagram",
    })

    if not state_record:
        return frontend_redirect("instagram", "error", "Invalid Instagram state")

    try:
        token_data = exchange_instagram_code_for_token(code)
        save_instagram_account(state_record["user"], token_data)
    except Exception as e:
        return frontend_redirect("instagram", "error", str(e))

    oauth_states_collection.delete_one({"_id": state_record["_id"]})
    return frontend_redirect("instagram", "success", "Instagram connected")


@router.get("/auth/facebook/start")
def start_facebook_auth(user=Depends(verify_token)):
    state = secrets.token_urlsafe(32)
    oauth_states_collection.insert_one({
        "state": state,
        "platform": "facebook",
        "user": user["sub"],
        "created_at": datetime.utcnow(),
    })

    return {"url": build_facebook_authorization_url(state)}


@router.get("/auth/facebook/callback")
def facebook_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    error_description: str = None,
):
    if error:
        return frontend_redirect("facebook", "error", error_description or error)

    if not code or not state:
        return frontend_redirect("facebook", "error", "Missing Facebook callback data")

    state_record = oauth_states_collection.find_one({
        "state": state,
        "platform": "facebook",
    })

    if not state_record:
        return frontend_redirect("facebook", "error", "Invalid Facebook state")

    try:
        token_data = exchange_facebook_code_for_token(code)
        save_facebook_account(state_record["user"], token_data)
    except Exception as e:
        return frontend_redirect("facebook", "error", str(e))

    oauth_states_collection.delete_one({"_id": state_record["_id"]})
    return frontend_redirect("facebook", "success", "Facebook connected")
