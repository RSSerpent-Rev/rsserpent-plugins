from xml.etree import ElementTree

import httpx
import pytest
from rsserpent_rev import app
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE
from rsserpent_rev.utils import HTTPClient
from starlette.testclient import TestClient


@pytest.mark.parametrize(
    ("path", "title"),
    [
        ("/bilibili/app/update/android", "1.2.3"),
        ("/bilibili/user/42/video", "Video"),
        ("/bilibili/user/42/bangumi", "Episode 1 - Series"),
        ("/bilibili/user/42/cinema", "Episode 1 - Series"),
    ],
)
def test_feed(path: str, title: str, monkeypatch: pytest.MonkeyPatch) -> None:
    responses = {
        "/x/v2/version": {"data": [{"version": "1.2.3", "desc": "Release", "ptime": 1717200000}]},
        "/x/space/acc/info": {
            "code": 0,
            "data": {"name": "Creator", "sign": "Channel"},
        },
        "/x/space/arc/search": {
            "code": 0,
            "data": {
                "list": {
                    "vlist": [
                        {
                            "title": "Video",
                            "description": "Example",
                            "bvid": "BV1",
                            "created": 1717200000,
                        }
                    ]
                }
            },
        },
        "/x/space/bangumi/follow/list": {
            "code": 0,
            "data": {
                "list": [
                    {
                        "new_ep": {"index_show": "Episode 1", "pub_time": "2024-06-01"},
                        "title": "Series",
                        "evaluate": "Example",
                        "season_id": 123,
                    }
                ]
            },
        },
    }

    async def get(_client: HTTPClient, url: str) -> httpx.Response:
        request = httpx.Request("GET", url)
        return httpx.Response(200, json=responses[request.url.path], request=request)

    monkeypatch.setattr(HTTPClient, "get", get)
    client = TestClient(app)
    rss = client.get(path)
    assert rss.status_code == 200
    assert rss.headers["Content-Type"] == RSS_MIMETYPE
    assert ElementTree.fromstring(rss.content).findtext("./channel/item/title") == title

    atom = client.get(path + ".atom")
    assert atom.status_code == 200
    assert atom.headers["Content-Type"] == ATOM_MIMETYPE
    assert ElementTree.fromstring(atom.content).tag == "{http://www.w3.org/2005/Atom}feed"
