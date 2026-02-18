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
        "printType": "books",
        "langRestrict": "en",
        "key": API_KEY,
    }

    resp = requests.get(GOOGLE_BOOKS_VOLUMES_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    results = []
    # API response might return "items": null; defensive programming here
    for item in data.get("items") or []:
        if not _is_valid_book(item):
            continue

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
        description = _shorten(description, 400)

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


def get_book_details(external_id: str) -> dict:
    """
    Use API ID to fetch details about a specific book and return normalized results.

    Args:
        external_id: Represents the API provided ID for the specific book
    """
    external_id = (external_id or "").strip()
    if not external_id:
        raise ValueError("external_id is required")

    url = f"{GOOGLE_BOOKS_VOLUMES_URL}/{external_id}"
    params = {"key": API_KEY}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    item = resp.json()

    info = item.get("volumeInfo") or {}
    title = info.get("title")
    authors = info.get("authors") or []
    published_date = info.get("publishedDate")
    image_links = info.get("imageLinks") or {}
    # Try to get the largest available image
    image_url = (
        image_links.get("large")
        or image_links.get("thumbnail")
        or image_links.get("medium")
        or image_links.get("small")
    )

    description = info.get("description")
    metadata = {
        "publisher": info.get("publisher"),
        "page_count": info.get("pageCount"),
    }

    return {
        "source": SOURCE,
        "external_id": external_id,
        "title": title,
        "authors": authors,
        "published_date": published_date,
        "image_url": image_url,
        "description": description,
        "total_units": info.get("pageCount"),
        "unit_type": "pages",
        "genres": info.get("categories") or [],
        "metadata": metadata,
    }


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


def _is_valid_book(volume):
    """
    Check if a volume from the Google Books API is a valid book with an ISBN.

    Args:
        volume (dict): A volume item from the Google Books API response

    Returns:
        bool: True if the volume has an ISBN identifier, False otherwise
    """
    info = volume.get("volumeInfo", {})
    identifiers = info.get("industryIdentifiers", [])
    if not any(i["type"] in ("ISBN_10", "ISBN_13") for i in identifiers):
        return False

    return True
