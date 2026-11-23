from xml.etree import ElementTree

import httpx
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE
from rsserpent_rev.testing import plugin_test_client

from rsserpent_plugins.csj_sdk_update import plugin


def test_feed() -> None:
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

    def respond(request: httpx.Request) -> httpx.Response:
        assert request.headers["cookie"] == "sid_guard=fixture-cookie"
        value = responses[str(request.url)]
        if isinstance(value, bytes):
            return httpx.Response(200, content=value)
        return httpx.Response(200, json=value)

    with plugin_test_client(
        plugin,
        transport=httpx.MockTransport(respond),
        settings={"sid_guard": "fixture-cookie"},
    ) as client:
        rss = client.get("/csj-sdk-update/197")
        assert rss.status_code == 200
        assert rss.headers["Content-Type"] == RSS_MIMETYPE
        root = ElementTree.fromstring(rss.content)
        assert "1.2.3" in (root.findtext("./channel/item/title") or "")
        atom = client.get("/csj-sdk-update/197.atom")
        assert atom.status_code == 200
        assert atom.headers["Content-Type"] == ATOM_MIMETYPE
        assert (
            ElementTree.fromstring(atom.content).tag
            == "{http://www.w3.org/2005/Atom}feed"
        )
