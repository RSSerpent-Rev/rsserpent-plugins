from xml.etree import ElementTree

import httpx
from rsserpent_rev.testing import plugin_test_client

from rsserpent_plugins.applovin_sdk_update import plugin


def test_route() -> None:
    """Return the iOS changelog from a fixed upstream response."""

    def respond(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://docs.applovin.com/max/api/1.0/changelog/ios"
        return httpx.Response(
            200,
            json=[
                {
                    "version": "1.2.3",
                    "published_at": "June 1, 2024",
                    "content": "Example release notes",
                },
                {
                    "version": "1.2.2",
                    "published_at": "May 1, 2024",
                    "content": "Previous release notes",
                },
            ],
        )

    with plugin_test_client(plugin, transport=httpx.MockTransport(respond)) as client:
        response = client.get("/applovin/sdk-update/ios.rss")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/xml;charset=utf-8"
        item, previous = ElementTree.fromstring(response.content).findall(
            "./channel/item"
        )
        assert "1.2.3" in (item.findtext("title") or "")
        assert item.findtext("description") == "Example release notes"

        assert item.findtext("link") == previous.findtext("link")
        rss_ids = [entry.findtext("guid") for entry in (item, previous)]
        assert rss_ids == ["urn:applovin:sdk:ios:1.2.3", "urn:applovin:sdk:ios:1.2.2"]
        atom = client.get("/applovin/sdk-update/ios.atom")
        assert atom.status_code == 200
        assert [
            entry.findtext("{*}id")
            for entry in ElementTree.fromstring(atom.content).findall("{*}entry")
        ] == rss_ids
