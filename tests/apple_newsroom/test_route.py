from xml.etree import ElementTree

import httpx
import pytest
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE
from rsserpent_rev.testing import plugin_test_client

from rsserpent_plugins.apple_newsroom import plugin


@pytest.mark.parametrize(
    "link",
    [
        "2024/06/example/",
        "/newsroom/2024/06/example/",
        "https://www.apple.com.cn/newsroom/2024/06/example/",
    ],
)
def test_feed(link: str) -> None:
    responses = {
        "https://www.apple.com.cn/newsroom/archive.json": {
            "results": [
                {
                    "result": [
                        {
                            "title": "New Apple release",
                            "link": link,
                            "description": "Release notes",
                            "date": "2024 \u5e74 6 \u6708 1 \u65e5",
                            "category": {"text": "Update"},
                        }
                    ]
                }
            ]
        }
    }

    def respond(request: httpx.Request) -> httpx.Response:
        value = responses[str(request.url)]
        if isinstance(value, bytes):
            return httpx.Response(200, content=value)
        return httpx.Response(200, json=value)

    with plugin_test_client(plugin, transport=httpx.MockTransport(respond)) as client:
        rss = client.get("/apple-newsroom")
        assert rss.status_code == 200
        assert rss.headers["Content-Type"] == RSS_MIMETYPE
        root = ElementTree.fromstring(rss.content)
        assert "New Apple release" in (root.findtext("./channel/item/title") or "")
        expected_url = "https://www.apple.com.cn/newsroom/2024/06/example/"
        assert root.findtext("./channel/item/link") == expected_url
        assert root.findtext("./channel/item/guid") == expected_url
        atom = client.get("/apple-newsroom.atom")
        assert atom.status_code == 200
        assert atom.headers["Content-Type"] == ATOM_MIMETYPE
        assert (
            ElementTree.fromstring(atom.content).tag
            == "{http://www.w3.org/2005/Atom}feed"
        )
        assert (
            ElementTree.fromstring(atom.content).findtext("{*}entry/{*}id")
            == expected_url
        )
