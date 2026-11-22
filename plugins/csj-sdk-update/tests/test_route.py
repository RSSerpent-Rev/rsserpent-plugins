from xml.etree import ElementTree

import httpx
import pytest
from rsserpent_rev import app
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE
from rsserpent_rev.utils import HTTPClient
from starlette.testclient import TestClient


def test_feed(monkeypatch: pytest.MonkeyPatch) -> None:
    responses = {
        "https://www.csjplatform.com/union_pangle/api/access_document/list?": {
            "data": {
                "list": [
                    {
                        "Id": 197,
                        "Name": "CSJ SDK",
                        "Log": '[{"UpdateVersion":"1.2.3","UpdateInfo":"Release notes","UpdateDate":"2024-06-01"}]',
                    }
                ]
            }
        }
    }

    async def get(_client: HTTPClient, url: str, **_kwargs: object) -> httpx.Response:
        value = responses[url]
        if isinstance(value, bytes):
            return httpx.Response(200, content=value, request=httpx.Request("GET", url))
        return httpx.Response(200, json=value, request=httpx.Request("GET", url))

    monkeypatch.setattr(HTTPClient, "get", get)
    client = TestClient(app)
    rss = client.get("/csj-sdk-update/197")
    assert rss.status_code == 200
    assert rss.headers["Content-Type"] == RSS_MIMETYPE
    root = ElementTree.fromstring(rss.content)
    assert "1.2.3" in (root.findtext("./channel/item/title") or "")
    atom = client.get("/csj-sdk-update/197.atom")
    assert atom.status_code == 200
    assert atom.headers["Content-Type"] == ATOM_MIMETYPE
    assert ElementTree.fromstring(atom.content).tag == "{http://www.w3.org/2005/Atom}feed"
