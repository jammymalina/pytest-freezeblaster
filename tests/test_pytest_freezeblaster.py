import re
from datetime import datetime


def test_freezing_time(testdir):
    testdir.makepyfile(
        """
        import pytest
        from datetime import date, datetime

        @pytest.mark.freeze_time('2017-05-20 15:42')
        def test_sth():
            assert datetime.now().date() == date(2017, 5, 20)
    """
    )

    result = testdir.runpytest("-v", "-s")
    assert result.ret == 0


def test_freezing_time_in_fixture(testdir):
    testdir.makepyfile(
        """
        import pytest
        from datetime import date, datetime

        @pytest.fixture
        def today():
            return datetime.now().date()

        @pytest.mark.freeze_time('2017-05-20 15:42')
        def test_sth(today):
            assert today == date(2017, 5, 20)
    """
    )

    result = testdir.runpytest("-v", "-s")
    assert result.ret == 0


def test_freezing_time_with_mark_and_fixture_used_by_test(testdir):
    # https://github.com/ktosiek/pytest-freezegun/issues/24
    testdir.makepyfile(
        """
        import pytest
        from datetime import date, datetime

        @pytest.fixture
        def today():
            return datetime.now().date()

        @pytest.mark.freeze_time('2017-05-20 15:42')
        def test_sth(today, freezer):
            assert today == date(2017, 5, 20)
    """
    )

    result = testdir.runpytest("-v", "-s")
    assert result.ret == 0


def test_no_mark(testdir):
    testdir.makepyfile(
        """
        import datetime

        def test_sth():
            assert datetime.datetime.now() > {}
    """.format(repr(datetime.now()))
    )

    result = testdir.runpytest("-v", "-s")
    assert result.ret == 0


def test_move_to(testdir):
    testdir.makepyfile(
        """
        from datetime import date
        import pytest

        @pytest.mark.freeze_time
        def test_changing_date(freezer):
            freezer.move_to('2017-05-20')
            assert date.today() == date(2017, 5, 20)
            freezer.move_to('2017-05-21')
            assert date.today() == date(2017, 5, 21)
    """
    )

    result = testdir.runpytest("-v", "-s")
    assert result.ret == 0


def test_fixture_durations(testdir):
    """
    In an older version, the time would be frozen for the pytest itself too.
    That caused it to report weird durations for test runs,
    namely very large numbers for setup and very large
    NEGATIVE numbers for teardown.
    """
    testdir.makepyfile(
        """
        import pytest
        from datetime import date, datetime

        def test_truth(freezer):
            freezer.move_to('2000-01-01')
            assert True
    """
    )

    result = testdir.runpytest("-vv", "-s", "--durations=3")

    # We don't have access to the actual terminalreporter,
    # so the only way to collect duration times is
    # to parse the pytest output.
    DURATION_REGEX = re.compile(
        r"""
        (-?\d+\.\d+)s          # Time in seconds
        \s+                    # Whitespace
        (call|setup|teardown)  # Test phase
        \s+                    # Whitespace
        test_fixture_durations.py::test_truth  # Test ID
    """,
        re.X,
    )

    durations = {}
    for line in result.outlines:
        match = DURATION_REGEX.match(line)
        if match is None:
            continue

        durations[match.group(2)] = float(match.group(1))

    # It should take a non-negative amount of time for each of the steps,
    # but it also should never take longer than a second
    assert 0 <= durations["setup"] <= 1
    assert 0 <= durations["call"] <= 1
    assert 0 <= durations["teardown"] <= 1


def test_marker_durations(testdir):
    """
    In an older version, the time would be frozen for the pytest itself too.
    That caused it to report weird durations for test runs,
    namely very large numbers for setup and very large
    NEGATIVE numbers for teardown.
    """
    testdir.makepyfile(
        """
        import pytest
        from datetime import date, datetime

        @pytest.mark.freeze_time('2000-01-01')
        def test_truth():
            assert True
    """
    )

    result = testdir.runpytest("-vv", "-s", "--durations=3")

    # We don't have access to the actual terminalreporter,
    # so the only way to collect duration times is
    # to parse the pytest output.
    DURATION_REGEX = re.compile(
        r"""
        (-?\d+\.\d+)s          # Time in seconds
        \s+                    # Whitespace
        (call|setup|teardown)  # Test phase
        \s+                    # Whitespace
        test_marker_durations.py::test_truth  # Test ID
    """,
        re.X,
    )

    durations = {}
    for line in result.outlines:
        match = DURATION_REGEX.match(line)
        if match is None:
            continue

        durations[match.group(2)] = float(match.group(1))

    # It should take a non-negative amount of time for each of the steps,
    # but it also should never take longer than a second
    assert 0 <= durations["setup"] <= 1
    assert 0 <= durations["call"] <= 1
    assert 0 <= durations["teardown"] <= 1


def test_fixture_no_mark(testdir):
    testdir.makepyfile(
        """
        from datetime import datetime
        import time

        def test_just_fixture(freezer):
            now = datetime.now()
            time.sleep(0.1)
            later = datetime.now()

            assert now == later
    """
    )

    result = testdir.runpytest("-v", "-s")
    assert result.ret == 0


def test_fixture_freezes_time(testdir):
    testdir.makepyfile(
        """
        import time

        def test_fixture_freezes_time(freezer):
            now = time.time()
            time.sleep(0.1)
            later = time.time()

            assert now == later
    """
    )

    result = testdir.runpytest("-v", "-s")
    assert result.ret == 0


def test_marker_freezes_time(testdir):
    testdir.makepyfile(
        """
        import pytest
        import time

        @pytest.mark.freeze_time('2000-01-01')
        def test_marker_freezes_time(freezer):
            now = time.time()
            time.sleep(0.1)
            later = time.time()

            assert now == later
    """
    )

    result = testdir.runpytest("-v", "-s")
    assert result.ret == 0


def test_class_freezing_time(testdir):
    testdir.makepyfile(
        """
        import pytest
        from datetime import date, datetime

        class TestAsClass(object):

            @pytest.mark.freeze_time('2017-05-20 15:42')
            def test_sth(self):
                assert datetime.now().date() == date(2017, 5, 20)
    """
    )

    result = testdir.runpytest("-v", "-s")
    assert result.ret == 0


def test_class_move_to(testdir):
    testdir.makepyfile(
        """
        from datetime import date
        import pytest

        class TestAsClass(object):

            @pytest.mark.freeze_time
            def test_changing_date(self, freezer):
                freezer.move_to('2017-05-20')
                assert date.today() == date(2017, 5, 20)
                freezer.move_to('2017-05-21')
                assert date.today() == date(2017, 5, 21)
    """
    )

    result = testdir.runpytest("-v", "-s")
    assert result.ret == 0


def test_class_just_fixture(testdir):
    testdir.makepyfile(
        """
        from datetime import datetime
        import time

        class TestAsClass(object):

            def test_just_fixture(self, freezer):
                now = datetime.now()
                time.sleep(0.1)
                later = datetime.now()

                assert now == later
    """
    )

    result = testdir.runpytest("-v", "-s")
    assert result.ret == 0


def test_pydantic(testdir):
    testdir.makepyfile(
        """
        from datetime import date, datetime, timezone
        import pydantic
        import pytest
        import time

        class DateModel(pydantic.BaseModel):
            current_datetime: datetime
            current_date: date

        class TestAsClass(object):

            @pytest.mark.freeze_time
            def test_changing_date(self, freezer):
                model = DateModel(
                    current_datetime=datetime.now(timezone.utc),
                    current_date=date.today(),
                )
                time.sleep(0.1)
                assert model.current_datetime == datetime.now(timezone.utc)
                assert model.current_date == date.today()

    """
    )

    result = testdir.runpytest("-v", "-s")
    assert result.ret == 0
