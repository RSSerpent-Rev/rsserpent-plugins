from xml.etree import ElementTree

import httpx
import pytest
from rsserpent_rev.utils import HTTPClient
from starlette.testclient import TestClient


def test_route(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Return the iOS changelog from a fixed upstream response."""

    async def get(_client: HTTPClient, url: str) -> httpx.Response:
        assert url == "https://docs.applovin.com/max/api/1.0/changelog/ios"
        return httpx.Response(
            200,
            json=[
                {
                    "version": "1.2.3",
                    "published_at": "June 1, 2024",
                    "content": "Example release notes",
                }
            ],
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(HTTPClient, "get", get)
    response = client.get("/applovin/sdk-update/ios.rss")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/xml;charset=utf-8"
    item = ElementTree.fromstring(response.content).find("./channel/item")
    assert item is not None
    assert "1.2.3" in (item.findtext("title") or "")
    assert item.findtext("description") == "Example release notes"
