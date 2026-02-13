import requests
import os
import time
from typing import Optional, Any


SOURCE = "igdb"
TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
IGDB_API_BASE = "https://api.igdb.com/v4"
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

# Token cache from igdb
_ACCESS_TOKEN: Optional[str] = None
_TOKEN_EXPIRES_AT: float = 0.0  # unix seconds


def search_games(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """
    Search for games using the IGDB API.

    Returns:
        List of normalized game dictionaries with keys:
            - source: API source identifier (always "igdb")
            - external_id: IGDB game ID (int)
            - title: Game title
            - year: Release year as int, or None
            - image_url: Cover image URL, or None
            - description: Short summary snippet (max 400 chars), or None
    """
    query = (query or "").strip()
    if not query:
        return []

    # IGDB uses POST with a query body
    body = "\n".join(
        [
            "fields id,name,first_release_date,summary,cover.image_id;",
            f'search "{_escape_igdb_search(query)}";',
            f"limit {int(max_results)};",
            f"where version_parent = null;",
        ]
    )

    items = _igdb_post_json("games", body)

    results: list[dict[str, Any]] = []
    for item in items or []:
        game_id = item.get("id")
        title = item.get("name")
        if not game_id or not title:
            continue

        cover = item.get("cover") or {}
        image_id = cover.get("image_id")
        image_url = _cover_url(image_id, size="t_thumb")
        description = _shorten(item.get("summary"), 400)

        results.append(
            {
                "source": SOURCE,
                "external_id": game_id,
                "title": title,
                "image_url": image_url,
                "description": description,
            }
        )

    return results


# ================================
# Helper funcs
# ================================


def _get_twitch_access_token() -> str:
    """
    Fetch and cache a Twitch App Access Token
    """
    # Need global when assigning values to globals, else python will treat it as a local variable.
    global _ACCESS_TOKEN, _TOKEN_EXPIRES_AT

    if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
        raise RuntimeError("Missing TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET env vars for IGDB auth")

    now = time.time()
    # Refresh Token if expired (With a 60 second buffer to account for minor discrepencies)
    if _ACCESS_TOKEN and now < (_TOKEN_EXPIRES_AT - 60):
        return _ACCESS_TOKEN

    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }

    resp = requests.post(TWITCH_TOKEN_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    token = data.get("access_token")
    expires_in = data.get("expires_in")  # seconds

    if not token or not expires_in:
        raise RuntimeError("Failed to obtain Twitch app access token")

    _ACCESS_TOKEN = token
    _TOKEN_EXPIRES_AT = now + float(expires_in)
    return token


def _igdb_post_json(resource: str, body: str) -> Any:
    """
    POST to IGDB and return JSON.
    resource: e.g. "games"
    body: IGDB query body string
    """
    token = _get_twitch_access_token()

    url = f"{IGDB_API_BASE}/{resource}"
    headers = {
        "Client-ID": TWITCH_CLIENT_ID or "",
        "Authorization": f"Bearer {token}",
    }

    resp = requests.post(url, data=body.encode("utf-8"), headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _shorten(text: Optional[str], max_len: int) -> Optional[str]:
    if not text:
        return None
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "…"


def _cover_url(image_id: Optional[str], size: str = "t_cover_big") -> Optional[str]:
    """
    IGDB images use image_id + a size slug.
    Example sizes: t_thumb, t_cover_small, t_cover_big, t_720p, t_1080p
    """
    if not image_id:
        return None
    return f"https://images.igdb.com/igdb/image/upload/{size}/{image_id}.jpg"


def _escape_igdb_search(s: str) -> str:
    """
    IGDB search uses double quotes; escape any that appear in user input.
    """
    return s.replace('"', '\\"')
