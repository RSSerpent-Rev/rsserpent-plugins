from xml.etree import ElementTree

import httpx
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE
from rsserpent_rev.testing import plugin_test_client

from rsserpent_plugins.admob_sdk_update import plugin


def test_feed() -> None:
    responses = {
        "https://developers.google.com/admob/ios/rel-notes": b"<table><tr><td>1.2.3</td><td>2024-06-01</td><td>Release notes</td></tr></table>"
    }

    def respond(request: httpx.Request) -> httpx.Response:
        value = responses[str(request.url)]
        if isinstance(value, bytes):
            return httpx.Response(200, content=value)
        return httpx.Response(200, json=value)

    with plugin_test_client(plugin, transport=httpx.MockTransport(respond)) as client:
        rss = client.get("/admob/sdk-update/ios")
        assert rss.status_code == 200
        assert rss.headers["Content-Type"] == RSS_MIMETYPE
        root = ElementTree.fromstring(rss.content)
        assert "AdMob SDK iOS 1.2.3 Update" in (
            root.findtext("./channel/item/title") or ""
        )
        atom = client.get("/admob/sdk-update/ios.atom")
        assert atom.status_code == 200
        assert atom.headers["Content-Type"] == ATOM_MIMETYPE
        assert (
            ElementTree.fromstring(atom.content).tag
            == "{http://www.w3.org/2005/Atom}feed"
        )
