import pytest

import ground_slash


def pytest_sessionstart(session):
    # set debug mode
    ground_slash.debug(True)
