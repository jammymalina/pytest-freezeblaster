import pytest
from freezeblaster import freeze_time

MARKER_NAME = "freeze_time"
FIXTURE_NAME = "freezer"


def get_closest_marker(node, name):
    """
    Get our marker, regardless of pytest version
    """
    return node.get_closest_marker("freeze_time")


@pytest.fixture(name=FIXTURE_NAME)
def freezer_fixture(request):
    """
    Freeze time and make it available to the test
    """
    args = []
    kwargs = {}
    ignore = []

    # If we've got a marker, use the arguments provided there
    marker = get_closest_marker(request.node, MARKER_NAME)
    if marker:
        ignore = marker.kwargs.pop("ignore", [])
        args = marker.args
        kwargs = marker.kwargs

    # Always want to ignore _pytest
    ignore.append("_pytest.terminal")
    ignore.append("_pytest.runner")

    # Freeze time around the test
    freezer = freeze_time(*args, ignore=ignore, **kwargs)
    frozen_time = freezer.start()
    yield frozen_time
    freezer.stop()


def pytest_collection_modifyitems(items):
    """
    Inject our fixture into any tests with our marker
    """
    for item in items:
        if get_closest_marker(item, MARKER_NAME):
            item.fixturenames.insert(0, FIXTURE_NAME)


def pytest_configure(config):
    """
    Register our marker
    """
    config.addinivalue_line("markers", "{}(...): use freezegun to freeze time".format(MARKER_NAME))
