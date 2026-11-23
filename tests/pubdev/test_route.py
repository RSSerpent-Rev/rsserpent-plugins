from xml.etree import ElementTree

import httpx
import pytest
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE
from rsserpent_rev.testing import plugin_test_client

from rsserpent_plugins.pubdev import plugin


@pytest.mark.parametrize(
    "package", ["example", "_fe_analyzer_shared", "_discoveryapis_commons"]
)
def test_feed(package: str) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        if request.url.path == f"/packages/{package}/changelog":
            return httpx.Response(
                200,
                text='<div class="changelog-entry"><h2>1.2.3</h2><div class="changelog-content">Release notes</div></div>',
            )
        assert request.url.path == f"/packages/{package}/versions"
        return httpx.Response(
            200,
            text=(
                f'<table><tbody><tr><td><a href="/packages/{package}/versions/1.2.3">1.2.3</a></td>'
                '<td></td><td></td><td><a data-timestamp="1717200000000">date</a></td></tr></tbody></table>'
            ),
        )

    with plugin_test_client(plugin, transport=httpx.MockTransport(respond)) as client:
        url = f"/pubdev/update/{package}"
        for suffix in ("", ".rss"):
            rss = client.get(url + suffix)
            assert rss.status_code == 200
            assert rss.headers["Content-Type"] == RSS_MIMETYPE
            assert (
                ElementTree.fromstring(rss.content).findtext("./channel/item/title")
                == f"{package} 1.2.3 更新"
            )
        atom = client.get(url + ".atom")
        assert atom.status_code == 200
        assert atom.headers["Content-Type"] == ATOM_MIMETYPE
        assert (
            ElementTree.fromstring(atom.content).findtext("{*}entry/{*}title")
            == f"{package} 1.2.3 更新"
        )


@pytest.mark.parametrize("package", ["2bad", "bad-name"])
def test_invalid_package_is_rejected_before_fetching(package: str) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        pytest.fail(f"Unexpected upstream request for {request.url}")

    with plugin_test_client(plugin, transport=httpx.MockTransport(respond)) as client:
        for suffix in ("", ".rss", ".atom"):
            assert client.get(f"/pubdev/update/{package}{suffix}").status_code == 400
