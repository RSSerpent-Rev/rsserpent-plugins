import pytest
from rsserpent_rev.main import create_app
from starlette.testclient import TestClient

from rsserpent_plugins.applovin_sdk_update import plugin


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Share one test client across the whole module with `pytest.fixture`."""
    return TestClient(create_app([plugin]))
