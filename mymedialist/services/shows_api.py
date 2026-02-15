import os
from typing import Any, Dict, List, Optional, Tuple

import requests

SOURCE = "tmdb"
TMDB_API_BASE = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/"
POSTER_SIZE_LIST = "w342"     # Obtained from https://developer.themoviedb.org/reference/configuration-details
POSTER_SIZE_DETAILS = "w500"
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")


def _tmdb_get(path: str, *, params: Optional[dict] = None, timeout: int = 10) -> Optional[dict]:
    """
    Perform an authenticated GET request to the TMDb API.

    Args:
        path: API path beginning with '/' (e.g., '/search/multi').
        params: Optional query parameters.
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as dict on success, otherwise None.
    """
    if not TMDB_ACCESS_TOKEN:
        return None

    headers = {
        "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}",
        "Accept": "application/json",
    }

    url = f"{TMDB_API_BASE}{path}"

    try:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def _year_from_date(date_str: Optional[str]) -> Optional[int]:
    """
    Extract year from ISO date string (YYYY-MM-DD).
    """
    if not date_str:
        return None
    try:
        return int(date_str.split("-", 1)[0])
    except (ValueError, AttributeError):
        return None


def _build_image_url(poster_path: Optional[str], *, size: str) -> Optional[str]:
    """
    Construct full TMDb image URL from poster path.
    """
    if not poster_path:
        return None
    return f"{IMAGE_BASE}{size}{poster_path}"


def _normalize_multi_result(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Normalize a TMDb /search/multi result into project standard format. 

    Returns:
        Normalized media dictionary or None if unsupported media type.
    """
    media_type = item.get("media_type")
    if media_type not in ("tv", "movie"):
        return None

    raw_id = item.get("id")
    if raw_id is None:
        return None

    if media_type == "tv":
        title = (item.get("name") or "").strip()
        year = _year_from_date(item.get("first_air_date"))
    else:
        title = (item.get("title") or "").strip()
        year = _year_from_date(item.get("release_date"))

    if not title:
        return None

    return {
        "source": SOURCE,
        "external_id": f"{media_type}:{raw_id}",
        "title": title,
        "authors": [],
        "year": year,
        "image_url": _build_image_url(item.get("poster_path"), size=POSTER_SIZE_LIST),
        "description": item.get("overview") or None,
        "meta": {
            "media_type": media_type,
        },
    }


def search_shows(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search TMDb for TV series and movies using /search/multi.

    Args:
        query: Search string.
        max_results: Maximum number of normalized results.

    Returns:
        List of normalized media dictionaries.
    """
    query = (query or "").strip()
    if not query:
        return []

    data = _tmdb_get(
        "/search/multi",
        params={"query": query, "include_adult": "false", "page": 1},
    )

    if not data:
        return []

    results = data.get("results") or []

    normalized: List[Dict[str, Any]] = []
    for item in results:
        norm = _normalize_multi_result(item)
        if norm:
            normalized.append(norm)
        if len(normalized) >= max_results:
            break

    return normalized


def _parse_external_id(external_id: str) -> Optional[Tuple[str, str]]:
    """
    Parse prefixed external_id into (media_type, id).
    """
    if not external_id or ":" not in external_id:
        return None

    media_type, raw_id = external_id.split(":", 1)

    if media_type not in ("tv", "movie") or not raw_id.isdigit():
        return None

    return media_type, raw_id


def get_show_or_movie_details(external_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve detailed metadata for a TV series or movie.

    Progress Model:
        TV     → total_units = number_of_episodes
        Movie  → total_units = 1

    Args:
        external_id: Prefixed identifier (e.g., 'tv:123', 'movie:456').

    Returns:
        Normalized detail dictionary or None on failure.
    """
    parsed = _parse_external_id(external_id)
    if not parsed:
        return None

    media_type, raw_id = parsed

    if media_type == "tv":
        data = _tmdb_get(f"/tv/{raw_id}")
        if not data:
            return None

        total_units = data.get("number_of_episodes")
        total_units = int(total_units) if isinstance(total_units, int) else None

        return {
            "source": SOURCE,
            "external_id": external_id,
            "title": (data.get("name") or "").strip(),
            "authors": [],
            "year": _year_from_date(data.get("first_air_date")),
            "image_url": _build_image_url(data.get("poster_path"), size=POSTER_SIZE_DETAILS),
            "description": data.get("overview") or None,
            "total_units": total_units,
            "unit_type": "episodes",
            "meta": {
                "media_type": "tv",
                "number_of_seasons": data.get("number_of_seasons"),
                "status": data.get("status"),
                "genres": [g["name"] for g in (data.get("genres") or []) if g.get("name")],
            },
        }

    # Movie branch
    data = _tmdb_get(f"/movie/{raw_id}")
    if not data:
        return None

    return {
        "source": SOURCE,
        "external_id": external_id,
        "title": (data.get("title") or "").strip(),
        "authors": [],
        "year": _year_from_date(data.get("release_date")),
        "image_url": _build_image_url(data.get("poster_path"), size=POSTER_SIZE_DETAILS),
        "description": data.get("overview") or None,
        "total_units": 1,
        "unit_type": "entries",
        "meta": {
            "media_type": "movie",
            "status": data.get("status"),
            "genres": [g["name"] for g in (data.get("genres") or []) if g.get("name")],
        },
    }