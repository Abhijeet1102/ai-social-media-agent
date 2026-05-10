from datetime import datetime, timedelta
from urllib.parse import urlencode

from fastapi import HTTPException

from app.config import (
    LINKEDIN_CLIENT_ID,
    LINKEDIN_CLIENT_SECRET,
    LINKEDIN_REDIRECT_URI,
    LINKEDIN_SCOPE,
    LINKEDIN_VERSION,
)
from app.database import connected_accounts_collection
from app.utils.http import get_json, post_form, post_json


def build_authorization_url(state: str):
    if not LINKEDIN_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="LINKEDIN_CLIENT_ID missing in backend .env",
        )

    params = urlencode({
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "state": state,
        "scope": LINKEDIN_SCOPE,
    })

    return f"https://www.linkedin.com/oauth/v2/authorization?{params}"


def exchange_code_for_token(code: str):
    if not LINKEDIN_CLIENT_ID or not LINKEDIN_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="LinkedIn credentials missing")

    return post_form(
        "https://www.linkedin.com/oauth/v2/accessToken",
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": LINKEDIN_REDIRECT_URI,
            "client_id": LINKEDIN_CLIENT_ID,
            "client_secret": LINKEDIN_CLIENT_SECRET,
        },
    )


def fetch_userinfo(access_token: str):
    return get_json(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )


def save_linkedin_account(username: str, token_data: dict):
    access_token = token_data.get("access_token")
    userinfo = fetch_userinfo(access_token) if access_token else {}
    expires_in = token_data.get("expires_in", 0)
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    provider_user_id = userinfo.get("sub")

    connected_accounts_collection.update_one(
        {
            "user": username,
            "platform": "linkedin",
        },
        {
            "$set": {
                "platform": "linkedin",
                "user": username,
                "access_token": access_token,
                "id_token": token_data.get("id_token"),
                "expires_in": expires_in,
                "expires_at": expires_at,
                "connected_at": datetime.utcnow(),
                "status": "connected",
                "scope": LINKEDIN_SCOPE,
                "provider_user_id": provider_user_id,
                "author_urn": f"urn:li:person:{provider_user_id}" if provider_user_id else None,
                "profile": {
                    "name": userinfo.get("name"),
                    "email": userinfo.get("email"),
                    "picture": userinfo.get("picture"),
                },
            }
        },
        upsert=True,
    )


def publish_text_post(account: dict, content: str):
    scope = account.get("scope", "")
    if "w_member_social" not in scope.split():
        raise HTTPException(
            status_code=403,
            detail="LinkedIn posting needs w_member_social. Enable Share on LinkedIn and reconnect.",
        )

    author_urn = account.get("author_urn")
    if not author_urn:
        raise HTTPException(status_code=400, detail="LinkedIn author URN missing. Reconnect account.")

    payload = {
        "author": author_urn,
        "commentary": content,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    _, headers = post_json(
        "https://api.linkedin.com/rest/posts",
        payload,
        headers={
            "Authorization": f"Bearer {account.get('access_token')}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Linkedin-Version": LINKEDIN_VERSION,
        },
    )

    return headers.get("x-restli-id")
