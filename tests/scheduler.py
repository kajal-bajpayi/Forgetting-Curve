"""Tests for the spaced-repetition scheduling engine."""

from datetime import datetime, timedelta, timezone

import pytest

from app.services.scheduler import (
    RecallRating,
    calculate_next_review,
)


FIXED_NOW = datetime(2026, 10, 14, 10, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    ("rating", "previous_interval", "expected_interval"),
    [
        (RecallRating.AGAIN, 1440, 10),
        (RecallRating.HARD, 1440, 1728),
        (RecallRating.GOOD, 1440, 2880),
        (RecallRating.EASY, 1440, 4320),
    ],
)
def test_rating_calculates_correct_interval(
    rating,
    previous_interval,
    expected_interval,
):
    result = calculate_next_review(
        rating=rating,
        previous_interval_minutes=previous_interval,
        now=FIXED_NOW,
    )

    assert result.interval_minutes == expected_interval
    assert result.next_review_at == (
        FIXED_NOW + timedelta(minutes=expected_interval)
    )


def test_first_review_uses_one_day_baseline():
    result = calculate_next_review(
        rating=RecallRating.GOOD,
        now=FIXED_NOW,
    )

    assert result.interval_minutes == 2880


def test_hard_rating_has_minimum_interval():
    result = calculate_next_review(
        rating=RecallRating.HARD,
        previous_interval_minutes=10,
        now=FIXED_NOW,
    )

    assert result.interval_minutes == 30


def test_maximum_interval_is_respected():
    result = calculate_next_review(
        rating=RecallRating.EASY,
        previous_interval_minutes=100000,
        max_interval_days=2,
        now=FIXED_NOW,
    )

    assert result.interval_minutes == 2880


@pytest.mark.parametrize("interval", [0, -1, True])
def test_invalid_previous_interval_is_rejected(interval):
    with pytest.raises(ValueError):
        calculate_next_review(
            rating=RecallRating.GOOD,
            previous_interval_minutes=interval,
            now=FIXED_NOW,
        )


def test_naive_datetime_is_rejected():
    naive_time = datetime(2026, 10, 14, 10, 0)

    with pytest.raises(ValueError):
        calculate_next_review(
            rating=RecallRating.GOOD,
            previous_interval_minutes=1440,
            now=naive_time,
        )


def test_invalid_rating_is_rejected():
    with pytest.raises(ValueError):
        calculate_next_review(
            rating="excellent",
            previous_interval_minutes=1440,
            now=FIXED_NOW,
        )