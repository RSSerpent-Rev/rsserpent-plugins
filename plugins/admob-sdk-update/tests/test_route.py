from xml.etree import ElementTree

import httpx
import pytest
from rsserpent_rev import app
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE
from rsserpent_rev.utils import HTTPClient
from starlette.testclient import TestClient


def test_feed(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = {
        "https://developers.google.com/admob/ios/rel-notes": b"<table><tr><td>1.2.3</td><td>2024-06-01</td><td>Release notes</td></tr></table>"
    }

    async def get(_client: HTTPClient, url: str, **_kwargs: object) -> httpx.Response:
        value = responses[url]
        if isinstance(value, bytes):
            return httpx.Response(200, content=value, request=httpx.Request("GET", url))
        return httpx.Response(200, json=value, request=httpx.Request("GET", url))

    monkeypatch.setattr(HTTPClient, "get", get)
    client = TestClient(app)
    rss = client.get("/admob/sdk-update/ios")
    assert rss.status_code == 200
    assert rss.headers["Content-Type"] == RSS_MIMETYPE
    root = ElementTree.fromstring(rss.content)
    assert "AdMob SDK iOS 1.2.3 Update" in (root.findtext("./channel/item/title") or "")
    atom = client.get("/admob/sdk-update/ios.atom")
    assert atom.status_code == 200
    assert atom.headers["Content-Type"] == ATOM_MIMETYPE
    assert ElementTree.fromstring(atom.content).tag == "{http://www.w3.org/2005/Atom}feed"
