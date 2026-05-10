from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import HTTPException

from app.config import (
    YOUTUBE_CLIENT_ID,
    YOUTUBE_CLIENT_SECRET,
    YOUTUBE_REDIRECT_URI,
    YOUTUBE_SCOPE,
)
from app.database import connected_accounts_collection
from app.utils.http import get_json, post_form


def build_authorization_url(state: str):
    if not YOUTUBE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="YOUTUBE_CLIENT_ID missing in backend .env",
        )

    params = urlencode({
        "client_id": YOUTUBE_CLIENT_ID,
        "redirect_uri": YOUTUBE_REDIRECT_URI,
        "response_type": "code",
        "scope": YOUTUBE_SCOPE,
        "access_type": "offline",
        "include_granted_scopes": "true",
        "state": state,
        "prompt": "consent",
    })

    return f"https://accounts.google.com/o/oauth2/v2/auth?{params}"


def exchange_code_for_token(code: str):
    if not YOUTUBE_CLIENT_ID or not YOUTUBE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="YouTube credentials missing")

    return post_form(
        "https://oauth2.googleapis.com/token",
        {
            "code": code,
            "client_id": YOUTUBE_CLIENT_ID,
            "client_secret": YOUTUBE_CLIENT_SECRET,
            "redirect_uri": YOUTUBE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    )


def fetch_channel(access_token: str):
    data = get_json(
        "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    items = data.get("items", [])
    return items[0] if items else {}


def save_youtube_account(username: str, token_data: dict):
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    channel = fetch_channel(access_token) if access_token else {}
    snippet = channel.get("snippet", {})
    expires_in = token_data.get("expires_in", 0)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    update_fields = {
        "platform": "youtube",
        "user": username,
        "access_token": access_token,
        "expires_in": expires_in,
        "expires_at": expires_at,
        "connected_at": datetime.utcnow(),
        "status": "connected",
        "scope": token_data.get("scope", YOUTUBE_SCOPE),
        "provider_user_id": channel.get("id"),
        "profile": {
            "name": snippet.get("title"),
            "email": None,
            "picture": snippet.get("thumbnails", {}).get("default", {}).get("url"),
        },
    }

    if refresh_token:
        update_fields["refresh_token"] = refresh_token

    connected_accounts_collection.update_one(
        {
            "user": username,
            "platform": "youtube",
        },
        {"$set": update_fields},
        upsert=True,
    )
