from datetime import UTC, date, datetime, time, timedelta, timezone
from time import sleep

from common.domain.value_objects.datetime import DateTime
from common.infrastructure.services.clock import FixedClock, SystemClock


class TestSystemClock:
    def test_system_clock_now_returns_current_utc_time(self):
        clock = SystemClock()
        now = clock.now()
        assert isinstance(now, DateTime)
        assert now.value.tzinfo == UTC
        assert abs(now - datetime.now(UTC)) < timedelta(
            seconds=1
        )  # Normally always true

    def test_clock_combine_uses_time_timezone(self):
        clock = SystemClock()
        combined = clock.combine(date(2025, 6, 12), time(10, 30, tzinfo=UTC))
        assert combined == datetime(2025, 6, 12, 10, 30, tzinfo=UTC)

    def test_system_clock_now_returns_utc_datetime(self):
        clock = SystemClock()
        now = clock.now()
        assert isinstance(now, DateTime)
        assert now.value.tzinfo == UTC
        assert abs(now - datetime.now(UTC)) < timedelta(seconds=1)

    def test_system_clock_now_returns_different_times(self):
        clock = SystemClock()
        first = clock.now()
        sleep(0.001)
        second = clock.now()

        assert second >= first

    def test_system_returns_proper_timezone(self):
        clock = SystemClock()

        assert clock.timezone() == clock._tzinfo  # type: ignore


class TestFixedClock:
    def test_fixed_clock_returns_same_time_each_call(self):
        fixed_time = datetime(2025, 6, 12, 12, 0, 0, tzinfo=UTC)
        clock = FixedClock(fixed_time)
        assert clock.now() == fixed_time
        assert clock.now() == fixed_time

    def test_fixed_clock_sets_utc_tzinfo_if_missing(self):
        naive_time = datetime(2025, 6, 12, 9, 0, 0)  # no tzinfo
        clock = FixedClock(naive_time)
        result = clock.now()
        assert result.value.tzinfo == UTC

    def test_fixed_clock_replaces_non_utc_tzinfo(self):
        other_tz = timezone(timedelta(hours=3))
        local_time = datetime(2025, 6, 12, 15, 0, 0, tzinfo=other_tz)
        clock = FixedClock(local_time)
        result = clock.now()
        assert result.value.tzinfo == UTC
