from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import HTTPException

from app.config import (
    INSTAGRAM_CLIENT_ID,
    INSTAGRAM_CLIENT_SECRET,
    INSTAGRAM_REDIRECT_URI,
    INSTAGRAM_SCOPE,
)
from app.database import connected_accounts_collection
from app.utils.http import get_json, post_form


def build_authorization_url(state: str):
    if not INSTAGRAM_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="INSTAGRAM_CLIENT_ID missing in backend .env",
        )

    params = urlencode({
        "client_id": INSTAGRAM_CLIENT_ID,
        "redirect_uri": INSTAGRAM_REDIRECT_URI,
        "response_type": "code",
        "scope": INSTAGRAM_SCOPE,
        "state": state,
        "enable_fb_login": "0",
        "force_authentication": "1",
    })

    return f"https://www.instagram.com/oauth/authorize?{params}"


def exchange_code_for_token(code: str):
    if not INSTAGRAM_CLIENT_ID or not INSTAGRAM_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Instagram credentials missing")

    return post_form(
        "https://api.instagram.com/oauth/access_token",
        {
            "client_id": INSTAGRAM_CLIENT_ID,
            "client_secret": INSTAGRAM_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": INSTAGRAM_REDIRECT_URI,
            "code": code,
        },
    )


def exchange_for_long_lived_token(short_lived_token: str):
    params = urlencode({
        "grant_type": "ig_exchange_token",
        "client_secret": INSTAGRAM_CLIENT_SECRET,
        "access_token": short_lived_token,
    })
    return get_json(f"https://graph.instagram.com/access_token?{params}")


def fetch_profile(access_token: str):
    params = urlencode({
        "fields": "user_id,username,account_type,profile_picture_url",
        "access_token": access_token,
    })
    return get_json(f"https://graph.instagram.com/v22.0/me?{params}")


def save_instagram_account(username: str, token_data: dict):
    short_lived_token = token_data.get("access_token")
    long_lived_data = exchange_for_long_lived_token(short_lived_token)
    access_token = long_lived_data.get("access_token", short_lived_token)
    profile = fetch_profile(access_token) if access_token else {}
    expires_in = long_lived_data.get("expires_in", 0)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    connected_accounts_collection.update_one(
        {
            "user": username,
            "platform": "instagram",
        },
        {
            "$set": {
                "platform": "instagram",
                "user": username,
                "access_token": access_token,
                "expires_in": expires_in,
                "expires_at": expires_at,
                "connected_at": datetime.utcnow(),
                "status": "connected",
                "scope": INSTAGRAM_SCOPE,
                "provider_user_id": profile.get("user_id") or profile.get("id"),
                "profile": {
                    "name": profile.get("username"),
                    "email": None,
                    "picture": profile.get("profile_picture_url"),
                    "account_type": profile.get("account_type"),
                },
            }
        },
        upsert=True,
    )
