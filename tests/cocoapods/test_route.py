import asyncio
from io import BytesIO
from xml.etree import ElementTree

import httpx
import pytest
from rsserpent_rev.main import RSS_MIMETYPE, create_app
from rsserpent_rev.utils import HTTPClient
from rsserpent_rev.utils.cache import get_cache
from starlette.testclient import TestClient

from rsserpent_plugins.cocoapods import github_release, plugin, route

FEED = b"""<feed xmlns="http://www.w3.org/2005/Atom"><title>Versions</title>
<id>https://github.com/example/project</id><link href="https://github.com/example/project"/>
<updated>2024-01-01T00:00:00Z</updated><entry><title>Version 1</title>
<id>https://github.com/example/project/releases/1</id><updated>2024-01-01T00:00:00Z</updated>
<link href="https://github.com/example/project/releases/1"/><content>First version</content></entry></feed>"""


@pytest.fixture(autouse=True)
def clear_provider_cache():
    cache = get_cache(route.provider)
    assert cache is not None
    cache.clear()


def test_releases_and_specs_fallback_share_client(monkeypatch):
    requests = []
    parse_feed = github_release.feedparser.parse

    def parse(source, **kwargs):
        assert isinstance(source, BytesIO)
        return parse_feed(source, **kwargs)

    monkeypatch.setattr(github_release.feedparser, "parse", parse)

    async def get(client, url):
        requests.append((client, url))
        content = FEED
        if url.startswith("https://cocoapods.org/"):
            repo = "https://github.com/example/project" if url.endswith("/Project") else "https://example.org/project"
            content = f'<ul class="links"><li><a href="{repo}">Repository</a></li></ul>'.encode()
        return httpx.Response(200, content=content, request=httpx.Request("GET", url))

    monkeypatch.setattr(HTTPClient, "get", get)
    with TestClient(create_app([plugin])) as client:
        for name in ("Project", "OtherProject"):
            response = client.get(f"/cocoapods/{name}")
            assert response.status_code == 200
            assert response.headers["Content-Type"] == RSS_MIMETYPE
            root = ElementTree.fromstring(response.content)
            assert root.findtext("./channel/title") == f"{name} Changelog"
            assert root.findtext("./channel/item/description") == "First version"

    assert requests[1][1] == "https://github.com/example/project/releases.atom"
    assert requests[3][1].startswith("https://github.com/CocoaPods/Specs/")
    assert all(client is requests[0][0] for client, _ in requests)
    assert requests[0][0].is_closed


@pytest.mark.parametrize(("upstream_status", "result"), [(404, 404), (503, 502), (200, 502)])
def test_missing_or_unavailable_pod(monkeypatch, upstream_status, result):
    async def get(client, url):
        return httpx.Response(upstream_status, request=httpx.Request("GET", url))

    monkeypatch.setattr(HTTPClient, "get", get)
    with TestClient(create_app([plugin])) as client:
        assert client.get("/cocoapods/Project").status_code == result


@pytest.mark.asyncio
async def test_pending_specs_request_keeps_service_responsive(monkeypatch):
    entered = asyncio.Event()
    release = asyncio.Event()

    async def get(client, url):
        request = httpx.Request("GET", url)
        if url.startswith("https://cocoapods.org/"):
            return httpx.Response(404, request=request)
        entered.set()
        await release.wait()
        return httpx.Response(200, content=FEED, request=request)

    monkeypatch.setattr(HTTPClient, "get", get)
    transport = httpx.ASGITransport(app=create_app([plugin]))
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        fetching = asyncio.create_task(client.get("/cocoapods/Project"))
        try:
            await asyncio.wait_for(entered.wait(), timeout=2)
            assert (await asyncio.wait_for(client.get("/"), timeout=2)).status_code == 200
            assert not fetching.done()
        finally:
            release.set()
            response = await fetching
    assert response.status_code == 200


@pytest.mark.parametrize(
    ("pod", "sdk_module", "platform"),
    [
        ("AppLovinSDK", route.applovin_sdk_update, "ios"),
        ("Google-Mobile-Ads-SDK", route.admob_sdk_update, "ios"),
        ("Ads-CN-Beta", route.csj_sdk_update, 197),
    ],
)
def test_sdk_dispatch(monkeypatch, pod, sdk_module, platform):
    async def get_feed(requested_platform):
        assert requested_platform == platform
        return {
            "title": "SDK release",
            "link": "https://example.org",
            "description": "Release notes",
            "items": [{"title": "Version 1"}],
        }

    monkeypatch.setattr(sdk_module, "provider", get_feed)
    with TestClient(create_app([plugin])) as client:
        rss = client.get(f"/cocoapods/{pod}.rss")
        assert rss.status_code == 200
        assert ElementTree.fromstring(rss.content).findtext("./channel/title") == "SDK release"
        atom = client.get(f"/cocoapods/{pod}.atom")
        assert atom.status_code == 200
        assert ElementTree.fromstring(atom.content).tag == "{http://www.w3.org/2005/Atom}feed"
