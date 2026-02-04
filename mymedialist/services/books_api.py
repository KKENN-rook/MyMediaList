from __future__ import annotations
from typing import Any, Optional
import requests
import os


GOOGLE_BOOKS_VOLUMES_URL = "https://www.googleapis.com/books/v1/volumes"
SOURCE = "google_books"
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")


def search_books(query: str, max_results: int = 10) -> list[dict[str, Any]]:
    """
    Search for books using the Google Books API.

    Args:
        query: Search term (book title, author, ISBN, etc.)
        max_results: Maximum number of results to return (default: 10)

    Returns:
        List of normalized book dictionaries with keys:
            - source: API source identifier (always "google_books")
            - external_id: Google Books volume ID
            - title: Book title
            - authors: List of author names (empty list if none)
            - year: Publication year as integer, or None
            - image_url: Cover image URL, or None
            - description: Shortened description (max 240 chars), or None

        Returns empty list if query is empty or API request fails.
    """
    query = (query or "").strip()
    if not query:
        return []

    params = {
        "q": query,
        "maxResults": max_results,
        "key": API_KEY,
    }

    try:
        resp = requests.get(GOOGLE_BOOKS_VOLUMES_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        print("Google Books error:", e)
        return []

    results = []
    # API response might return "items": null; defensive programming here
    for item in data.get("items") or []:
        volume_id = item.get("id")
        info = item.get("volumeInfo") or {}
        title = info.get("title")
        # Only want books that have volume_id and title
        if not volume_id or not title:
            continue

        authors = info.get("authors") or []
        year = int(info.get("publishedDate")[:4]) if info.get("publishedDate") else None

        image_links = info.get("imageLinks") or {}
        image_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")

        description = info.get("description")
        description = _shorten(description, 240)

        results.append(
            {
                "source": SOURCE,
                "external_id": volume_id,
                "title": title,
                "authors": authors,  # list[str]
                "year": year,  # int | None
                "image_url": image_url,  # str | None
                "description": description,  # str | None (short snippet)
            }
        )

    return results


def _shorten(text: Optional[str], max_len: int) -> Optional[str]:
    """
    Truncate text to a maximum length.

    Args:
        text: Text to shorten, or None
        max_len: Maximum character length

    Returns:
        Shortened text with ellipsis (…) if truncated, original text if
        shorter than max_len, or None if input text is None/empty.
    """
    if not text:
        return None
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "…"
