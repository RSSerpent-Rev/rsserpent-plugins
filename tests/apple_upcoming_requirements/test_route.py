from xml.etree import ElementTree

import httpx
import pytest
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE, create_app
from rsserpent_rev.utils import HTTPClient
from starlette.testclient import TestClient

from rsserpent_plugins.apple_upcoming_requirements import plugin


def test_feed(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = {
        "https://developer.apple.com/news/upcoming-requirements/": b'<section class="article-list"><article><a class="article-title" href="/news/example/">New submission requirements</a><span class="article-text">Release notes</span><p class="article-date">From June 1, 2024</p></article></section>'
    }

    async def get(_client: HTTPClient, url: str, **_kwargs: object) -> httpx.Response:
        value = responses[url]
        if isinstance(value, bytes):
            return httpx.Response(200, content=value, request=httpx.Request("GET", url))
        return httpx.Response(200, json=value, request=httpx.Request("GET", url))

    monkeypatch.setattr(HTTPClient, "get", get)
    client = TestClient(create_app([plugin]))
    rss = client.get("/apple-upcoming-requirements")
    assert rss.status_code == 200
    assert rss.headers["Content-Type"] == RSS_MIMETYPE
    root = ElementTree.fromstring(rss.content)
    assert "New submission requirements" in (root.findtext("./channel/item/title") or "")
    atom = client.get("/apple-upcoming-requirements.atom")
    assert atom.status_code == 200
    assert atom.headers["Content-Type"] == ATOM_MIMETYPE
    assert ElementTree.fromstring(atom.content).tag == "{http://www.w3.org/2005/Atom}feed"
