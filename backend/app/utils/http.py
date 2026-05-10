import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import HTTPException


def post_form(url: str, payload: dict):
    data = urlencode(payload).encode("utf-8")
    req = Request(
        url,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    return send_json_request(req)


def get_json(url: str, headers: dict = None):
    req = Request(url, headers=headers or {}, method="GET")
    return send_json_request(req)


def post_json(url: str, payload: dict, headers: dict = None):
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            **(headers or {}),
        },
        method="POST",
    )
    return send_json_request(req, return_headers=True)


def send_json_request(req: Request, return_headers: bool = False):
    try:
        with urlopen(req, timeout=15) as response:
            raw_body = response.read().decode("utf-8")
            body = json.loads(raw_body) if raw_body else {}
            if return_headers:
                return body, dict(response.headers)
            return body
    except HTTPError as e:
        detail = e.read().decode("utf-8")
        raise HTTPException(status_code=e.code, detail=detail)
    except URLError as e:
        raise HTTPException(status_code=502, detail=str(e))
