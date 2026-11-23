from xml.etree import ElementTree

import httpx
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE
from rsserpent_rev.testing import plugin_test_client

from rsserpent_plugins.slackware_news import plugin


def test_feed() -> None:
    responses = {
        "http://www.slackware.com/": b"<body><div><center><table><tr><td><b>Slackware update</b></td></tr><tr><td>Release notes</td><td><b>Sat Jun 1 04:44:56 UTC 2024</b></td></tr></table></center></div></body>"
    }

    def respond(request: httpx.Request) -> httpx.Response:
        value = responses[str(request.url)]
        if isinstance(value, bytes):
            return httpx.Response(200, content=value)
        return httpx.Response(200, json=value)

    with plugin_test_client(plugin, transport=httpx.MockTransport(respond)) as client:
        rss = client.get("/slackware-news")
        assert rss.status_code == 200
        assert rss.headers["Content-Type"] == RSS_MIMETYPE
        root = ElementTree.fromstring(rss.content)
        assert "Slackware update" in (root.findtext("./channel/item/title") or "")
        atom = client.get("/slackware-news.atom")
        assert atom.status_code == 200
        assert atom.headers["Content-Type"] == ATOM_MIMETYPE
        assert (
            ElementTree.fromstring(atom.content).tag
            == "{http://www.w3.org/2005/Atom}feed"
        )
