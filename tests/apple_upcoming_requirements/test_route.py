from xml.etree import ElementTree

import httpx
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE
from rsserpent_rev.testing import plugin_test_client

from rsserpent_plugins.apple_upcoming_requirements import plugin


def test_feed() -> None:
    responses = {
        "https://developer.apple.com/news/upcoming-requirements/": b'<section class="article-list"><article><a class="article-title" href="/news/example/">New submission requirements</a><span class="article-text">Release notes</span><p class="article-date">From June 1, 2024</p></article></section>'
    }

    def respond(request: httpx.Request) -> httpx.Response:
        value = responses[str(request.url)]
        if isinstance(value, bytes):
            return httpx.Response(200, content=value)
        return httpx.Response(200, json=value)

    with plugin_test_client(plugin, transport=httpx.MockTransport(respond)) as client:
        rss = client.get("/apple-upcoming-requirements")
        assert rss.status_code == 200
        assert rss.headers["Content-Type"] == RSS_MIMETYPE
        root = ElementTree.fromstring(rss.content)
        assert "New submission requirements" in (
            root.findtext("./channel/item/title") or ""
        )
        atom = client.get("/apple-upcoming-requirements.atom")
        assert atom.status_code == 200
        assert atom.headers["Content-Type"] == ATOM_MIMETYPE
        assert (
            ElementTree.fromstring(atom.content).tag
            == "{http://www.w3.org/2005/Atom}feed"
        )
