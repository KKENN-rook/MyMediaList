from sqlalchemy import select, func

from ..models import UserMedia, MediaWork
from ..shared_constants import STATUSES


def get_category_stats(session, *, user_id: int, category: str) -> dict:
    """
    Returns aggregate stats for one category(books/games/shows) for a given user
    """
    # Counts number of entries under specified category
    total = session.execute(
        select(func.count(UserMedia.id))
        .join(UserMedia.media)
        .where(
            UserMedia.user_id == user_id,
            MediaWork.category == category,
        )
    ).scalar_one()

    # Calculates average rating, null values not included
    avg_rating = session.execute(
        select(func.avg(UserMedia.rating))
        .join(UserMedia.media)
        .where(
            UserMedia.user_id == user_id,
            MediaWork.category == category,
            UserMedia.rating.isnot(None),
        )
    ).scalar()

    # Status Counts
    rows = session.execute(
        select(UserMedia.status, func.count(UserMedia.id))
        .join(UserMedia.media)
        .where(
            UserMedia.user_id == user_id,
            MediaWork.category == category,
        )
        .group_by(UserMedia.status)
    ).all()

    status_counts = {status: 0 for status in STATUSES}

    for status, count in rows:
        status_counts[status] = count

    return {
        "total": total,
        "avg_rating": round(float(avg_rating), 2) if avg_rating is not None else None,
        "status_counts": status_counts,
    }
