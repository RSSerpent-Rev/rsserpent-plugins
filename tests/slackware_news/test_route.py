from xml.etree import ElementTree

import httpx
import pytest
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE, create_app
from rsserpent_rev.utils import HTTPClient
from starlette.testclient import TestClient

from rsserpent_plugins.slackware_news import plugin


def test_feed(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = {
        "http://www.slackware.com/": b"<body><div><center><table><tr><td><b>Slackware update</b></td></tr><tr><td>Release notes</td><td><b>Sat Jun 1 04:44:56 UTC 2024</b></td></tr></table></center></div></body>"
    }

    async def get(_client: HTTPClient, url: str, **_kwargs: object) -> httpx.Response:
        value = responses[url]
        if isinstance(value, bytes):
            return httpx.Response(200, content=value, request=httpx.Request("GET", url))
        return httpx.Response(200, json=value, request=httpx.Request("GET", url))

    monkeypatch.setattr(HTTPClient, "get", get)
    client = TestClient(create_app([plugin]))
    rss = client.get("/slackware-news")
    assert rss.status_code == 200
    assert rss.headers["Content-Type"] == RSS_MIMETYPE
    root = ElementTree.fromstring(rss.content)
    assert "Slackware update" in (root.findtext("./channel/item/title") or "")
    atom = client.get("/slackware-news.atom")
    assert atom.status_code == 200
    assert atom.headers["Content-Type"] == ATOM_MIMETYPE
    assert ElementTree.fromstring(atom.content).tag == "{http://www.w3.org/2005/Atom}feed"
