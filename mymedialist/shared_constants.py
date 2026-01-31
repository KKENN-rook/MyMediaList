CATEGORY_TITLES = {
    "books": "Books",
    "games": "Games",
    "shows": "Shows & Film",
}

CATEGORIES = list(CATEGORY_TITLES.keys())

# Default keys are the actual values stored in the db; rest is for site-wide flavor text
STATUS_LABELS = {
    "default": {
        "in_progress": "In Progress",
        "completed": "Completed",
        "on_hold": "On Hold",
        "planned": "Planned",
        "dropped": "Dropped",
    },
    "books": {
        "in_progress": "Reading",
        "completed": "Read",
        "on_hold": "On Hold",
        "planned": "Plan to Read",
        "dropped": "Dropped",
    },
    "shows": {
        "in_progress": "Watching",
        "completed": "Completed",
        "on_hold": "On Hold",
        "planned": "Plan to Watch",
        "dropped": "Dropped",
    },
    "games": {
        "in_progress": "Playing",
        "completed": "Completed",
        "on_hold": "On Hold",
        "planned": "Plan to Play",
        "dropped": "Dropped",
    },
}

STATUSES = tuple(STATUS_LABELS["default"].keys())

def get_status_labels(category):
    return STATUS_LABELS.get(category, STATUS_LABELS["default"])