from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import HTTPException

from app.config import (
    FACEBOOK_CLIENT_ID,
    FACEBOOK_CLIENT_SECRET,
    FACEBOOK_GRAPH_VERSION,
    FACEBOOK_REDIRECT_URI,
    FACEBOOK_SCOPE,
)
from app.database import connected_accounts_collection
from app.utils.http import get_json


def graph_url(path: str):
    return f"https://graph.facebook.com/{FACEBOOK_GRAPH_VERSION}{path}"


def build_authorization_url(state: str):
    if not FACEBOOK_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="FACEBOOK_CLIENT_ID missing in backend .env",
        )

    params = urlencode({
        "client_id": FACEBOOK_CLIENT_ID,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
        "state": state,
        "response_type": "code",
        "scope": FACEBOOK_SCOPE,
    })

    return f"https://www.facebook.com/{FACEBOOK_GRAPH_VERSION}/dialog/oauth?{params}"


def exchange_code_for_token(code: str):
    if not FACEBOOK_CLIENT_ID or not FACEBOOK_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Facebook credentials missing")

    params = urlencode({
        "client_id": FACEBOOK_CLIENT_ID,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
        "client_secret": FACEBOOK_CLIENT_SECRET,
        "code": code,
    })
    return get_json(graph_url(f"/oauth/access_token?{params}"))


def exchange_for_long_lived_token(short_lived_token: str):
    params = urlencode({
        "grant_type": "fb_exchange_token",
        "client_id": FACEBOOK_CLIENT_ID,
        "client_secret": FACEBOOK_CLIENT_SECRET,
        "fb_exchange_token": short_lived_token,
    })
    return get_json(graph_url(f"/oauth/access_token?{params}"))


def fetch_profile(access_token: str):
    params = urlencode({
        "fields": "id,name,email,picture",
        "access_token": access_token,
    })
    return get_json(graph_url(f"/me?{params}"))


def fetch_pages(access_token: str):
    params = urlencode({
        "fields": "id,name,access_token,tasks",
        "access_token": access_token,
    })
    data = get_json(graph_url(f"/me/accounts?{params}"))
    return data.get("data", [])


def save_facebook_account(username: str, token_data: dict):
    short_lived_token = token_data.get("access_token")
    long_lived_data = exchange_for_long_lived_token(short_lived_token)
    access_token = long_lived_data.get("access_token", short_lived_token)
    profile = fetch_profile(access_token) if access_token else {}
    pages = fetch_pages(access_token) if access_token else []
    expires_in = long_lived_data.get("expires_in", token_data.get("expires_in", 0))
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    connected_accounts_collection.update_one(
        {
            "user": username,
            "platform": "facebook",
        },
        {
            "$set": {
                "platform": "facebook",
                "user": username,
                "access_token": access_token,
                "expires_in": expires_in,
                "expires_at": expires_at,
                "connected_at": datetime.utcnow(),
                "status": "connected",
                "scope": FACEBOOK_SCOPE,
                "provider_user_id": profile.get("id"),
                "profile": {
                    "name": profile.get("name"),
                    "email": profile.get("email"),
                    "picture": profile.get("picture", {}).get("data", {}).get("url"),
                },
                "pages": pages,
            }
        },
        upsert=True,
    )
