from datetime import UTC, datetime, timedelta

import pytest

from exceptions import (
    BookingAlreadyStartedException,
    BookingDateInPastException,
    CheckOutBeforeCheckInException,
    check_booking_not_in_past,
    check_booking_not_started,
    check_date_to_after_date_from,
)

TODAY = datetime.now(tz=UTC).date()


@pytest.mark.parametrize(
    "date_from, date_to",
    [
        (TODAY, TODAY),  # выезд в тот же день, что и заезд
        (TODAY, TODAY - timedelta(days=1)),  # выезд раньше заезда
    ],
)
def test_check_date_to_after_date_from_raises_for_invalid_range(date_from, date_to):
    with pytest.raises(CheckOutBeforeCheckInException):
        check_date_to_after_date_from(date_from, date_to)


def test_check_date_to_after_date_from_passes_for_valid_range():
    check_date_to_after_date_from(TODAY, TODAY + timedelta(days=1))


def test_check_booking_not_in_past_raises_for_yesterday():
    with pytest.raises(BookingDateInPastException):
        check_booking_not_in_past(TODAY - timedelta(days=1))


def test_check_booking_not_in_past_passes_for_today_and_future():
    check_booking_not_in_past(TODAY)
    check_booking_not_in_past(TODAY + timedelta(days=1))


def test_check_booking_not_started_raises_for_today_and_past():
    with pytest.raises(BookingAlreadyStartedException):
        check_booking_not_started(TODAY)
    with pytest.raises(BookingAlreadyStartedException):
        check_booking_not_started(TODAY - timedelta(days=1))


def test_check_booking_not_started_passes_for_future_date():
    check_booking_not_started(TODAY + timedelta(days=1))
