# pytest-freezeblaster

Wrap tests with fixtures in freeze_time

## Features

- Freeze time in both the test and fixtures
- Access the freezer when you need it

## Installation

You can install "pytest-freezeblaster" via `pip` from `PyPI`:

    $ pip install pytest-freezeblaster

## Usage

Freeze time by using the `freezer` fixture:

```python
    def test_frozen_date(freezer):
        now = datetime.now()
        time.sleep(1)
        later = datetime.now()
        assert now == later
```

This can then be used to move time:

```python
    def test_moving_date(freezer):
        now = datetime.now()
        freezer.move_to('2017-05-20')
        later = datetime.now()
        assert now != later
```

You can also pass arguments to freezegun by using the `freeze_time` mark:

```python
    @pytest.mark.freeze_time('2017-05-21')
    def test_current_date():
        assert date.today() == date(2017, 5, 21)
```

The `freezer` fixture and `freeze_time` mark can be used together,
and they work with other fixtures:

```python
    @pytest.fixture
    def current_date():
        return date.today()

    @pytest.mark.freeze_time
    def test_changing_date(current_date, freezer):
        freezer.move_to('2017-05-20')
        assert current_date == date(2017, 5, 20)
        freezer.move_to('2017-05-21')
        assert current_date == date(2017, 5, 21)
```

They can also be used in class-based tests:

```python
    class TestDate:
        @pytest.mark.freeze_time
        def test_changing_date(self, current_date, freezer):
            freezer.move_to('2017-05-20')
            assert current_date == date(2017, 5, 20)
            freezer.move_to('2017-05-21')
            assert current_date == date(2017, 5, 21)
```

## Credits

All credits go to [ktosiek](https://github.com/ktosiek).
