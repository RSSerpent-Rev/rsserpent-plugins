from xml.etree import ElementTree

import httpx
import pytest
from rsserpent_rev import app
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE
from rsserpent_rev.utils import HTTPClient
from starlette.testclient import TestClient


def test_feed(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = {
        "https://pub.dev/packages/example/changelog": b'<div class="changelog-entry"><h2>1.2.3</h2><div class="changelog-content">Release notes</div></div>',
        "https://pub.dev/packages/example/versions": b'<table><tbody><tr><td><a href="/packages/example/versions/1.2.3">1.2.3</a></td><td></td><td></td><td><a data-timestamp="1717200000000">date</a></td></tr></tbody></table>',
    }

    async def get(_client: HTTPClient, url: str, **_kwargs: object) -> httpx.Response:
        value = responses[url]
        if isinstance(value, bytes):
            return httpx.Response(200, content=value, request=httpx.Request("GET", url))
        return httpx.Response(200, json=value, request=httpx.Request("GET", url))

    monkeypatch.setattr(HTTPClient, "get", get)
    client = TestClient(app)
    rss = client.get("/pubdev/update/example")
    assert rss.status_code == 200
    assert rss.headers["Content-Type"] == RSS_MIMETYPE
    root = ElementTree.fromstring(rss.content)
    assert "example 1.2.3" in (root.findtext("./channel/item/title") or "")
    atom = client.get("/pubdev/update/example.atom")
    assert atom.status_code == 200
    assert atom.headers["Content-Type"] == ATOM_MIMETYPE
    assert ElementTree.fromstring(atom.content).tag == "{http://www.w3.org/2005/Atom}feed"
