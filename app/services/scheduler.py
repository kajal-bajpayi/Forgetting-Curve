"""Spaced-repetition scheduling engine."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from math import ceil


# Initial scheduling rules (configurable starting heuristics).
INITIAL_INTERVAL_MINUTES = 24 * 60
AGAIN_INTERVAL_MINUTES = 10
MIN_HARD_INTERVAL_MINUTES = 30
MAX_INTERVAL_DAYS = 180


class RecallRating(StrEnum):
    """Possible user ratings after reviewing a flashcard."""

    AGAIN = "again"
    HARD = "hard"
    GOOD = "good"
    EASY = "easy"


@dataclass(frozen=True)
class ScheduleResult:
    """Result returned by the scheduling calculation."""

    interval_minutes: int
    next_review_at: datetime


def calculate_next_review(
    rating: RecallRating,
    previous_interval_minutes: int | None = None,
    now: datetime | None = None,
    max_interval_days: int = MAX_INTERVAL_DAYS,
) -> ScheduleResult:
    """
    Calculate the next review interval and due timestamp.

    If no previous interval exists, use a one-day baseline.
    A new card's initial due time is managed separately and can
    be set to the current time when the card is created.
    """

    # 1. Validate the rating.
    if not isinstance(rating, RecallRating):
        raise ValueError("rating must be a RecallRating value")

    # 2. Validate the maximum interval.
    if (
        isinstance(max_interval_days, bool)
        or not isinstance(max_interval_days, int)
        or max_interval_days <= 0
    ):
        raise ValueError("max_interval_days must be a positive integer")

    # 3. Validate the previous interval when supplied.
    if previous_interval_minutes is not None:
        if (
            isinstance(previous_interval_minutes, bool)
            or not isinstance(previous_interval_minutes, int)
            or previous_interval_minutes <= 0
        ):
            raise ValueError(
                "previous_interval_minutes must be a positive integer"
            )

    # 4. Get the current time in timezone-aware UTC.
    if now is None:
        current_time = datetime.now(timezone.utc)
    else:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now must be timezone-aware")

        current_time = now.astimezone(timezone.utc)

    # 5. Use the initial baseline if this is the first review.
    previous_interval = (
        previous_interval_minutes
        if previous_interval_minutes is not None
        else INITIAL_INTERVAL_MINUTES
    )

    # 6. Calculate the next interval based on recall performance.
    if rating == RecallRating.AGAIN:
        interval_minutes = AGAIN_INTERVAL_MINUTES

    elif rating == RecallRating.HARD:
        interval_minutes = max(
            MIN_HARD_INTERVAL_MINUTES,
            ceil(previous_interval * 1.2),
        )

    elif rating == RecallRating.GOOD:
        interval_minutes = previous_interval * 2

    elif rating == RecallRating.EASY:
        interval_minutes = previous_interval * 3

    else:
        # Defensive check if the enum is extended in the future.
        raise ValueError(f"Unsupported recall rating: {rating}")

    # 7. Prevent the interval from exceeding the configured limit.
    max_interval_minutes = max_interval_days * 24 * 60

    interval_minutes = min(
        interval_minutes,
        max_interval_minutes,
    )

    # 8. Calculate the next due timestamp.
    next_review_at = current_time + timedelta(
        minutes=interval_minutes
    )

    return ScheduleResult(
        interval_minutes=interval_minutes,
        next_review_at=next_review_at,
    )