import asyncio
from contextlib import asynccontextmanager
from io import BytesIO
from types import SimpleNamespace
from urllib.parse import quote
from xml.etree import ElementTree

import aiohttp
import httpx
import pytest
from aiohttp.resolver import ThreadedResolver
from rsserpent_rev.main import ATOM_MIMETYPE, RSS_MIMETYPE, create_app
from rsserpent_rev.utils.cache import get_cache
from starlette.testclient import TestClient

from rsserpent_plugins.rss_proxy import plugin, route

SOURCE = "https://source.example/news.rss?edition=test"
PATH = "/proxy/" + quote(SOURCE, safe=":/")
FEED = b"""<rss version="2.0"><channel>
<title>Example news</title><link>https://source.example/</link>
<description>News feed</description><item><title>Example story</title>
<link>https://source.example/story</link><description>Story text</description></item>
</channel></rss>"""


async def chunks(body):
    yield body


@pytest.fixture(autouse=True)
def clear_feed_cache():
    cache = get_cache(route.fetch)
    assert cache is not None
    cache.clear()


def test_disabled_by_default(monkeypatch):
    monkeypatch.delenv("RSSERPENT_PROXY_SOURCES", raising=False)
    response = TestClient(create_app([plugin])).get(PATH)
    assert response.status_code == 404


def test_rss_and_atom_use_the_lifespan_client(monkeypatch):
    monkeypatch.setenv("RSSERPENT_PROXY_SOURCES", SOURCE)
    calls = []
    parse_feed = route.feedparser.parse

    def parse(source, **kwargs):
        assert isinstance(source, BytesIO)
        return parse_feed(source, **kwargs)

    monkeypatch.setattr(route.feedparser, "parse", parse)

    @asynccontextmanager
    async def get(client, url, *, allow_redirects):
        assert not allow_redirects and not client.trust_env
        calls.append((client, str(url)))
        yield SimpleNamespace(
            status=200,
            headers={},
            content_length=None,
            content=SimpleNamespace(iter_chunked=lambda _: chunks(FEED)),
        )

    monkeypatch.setattr(aiohttp.ClientSession, "get", get)
    with TestClient(create_app([plugin])) as client:
        rss = client.get(PATH)
        cache = get_cache(route.fetch)
        assert cache is not None
        cache.clear()
        atom = client.get(PATH, params={"format": "atom"})
        denied = client.get("/proxy/https://other.example/news.rss")

    assert rss.status_code == atom.status_code == 200
    assert rss.headers["Content-Type"] == RSS_MIMETYPE
    assert atom.headers["Content-Type"] == ATOM_MIMETYPE
    assert ElementTree.fromstring(rss.content).findtext("./channel/title") == "Example news"
    assert ElementTree.fromstring(atom.content).tag == "{http://www.w3.org/2005/Atom}feed"
    assert denied.status_code == 403
    assert [url for _, url in calls] == [SOURCE, SOURCE]
    assert calls[0][0] is calls[1][0]
    assert calls[0][0].closed


@pytest.mark.parametrize(("status", "body"), [(301, b""), (200, b"12")])
def test_redirect_and_stream_size(monkeypatch, status, body):
    monkeypatch.setenv("RSSERPENT_PROXY_SOURCES", SOURCE)
    monkeypatch.setattr(route, "MAX_FEED_BYTES", 1)
    urls = []

    @asynccontextmanager
    async def get(client, url, *, allow_redirects):
        assert not allow_redirects
        urls.append(url)
        yield SimpleNamespace(
            status=status,
            headers={"Location": "https://another.example/feed"},
            content_length=None,
            content=SimpleNamespace(iter_chunked=lambda _: chunks(body)),
        )

    monkeypatch.setattr(aiohttp.ClientSession, "get", get)
    with TestClient(create_app([plugin])) as client:
        assert client.get(PATH).status_code == 502
    assert len(urls) == 1


def test_upstream_timeout_returns_gateway_timeout(monkeypatch):
    monkeypatch.setenv("RSSERPENT_PROXY_SOURCES", SOURCE)

    def get(client, url, *, allow_redirects):
        raise asyncio.TimeoutError

    monkeypatch.setattr(aiohttp.ClientSession, "get", get)
    with TestClient(create_app([plugin])) as client:
        assert client.get(PATH).status_code == 504


@pytest.mark.asyncio
async def test_connector_uses_the_checked_resolver_result(monkeypatch):
    async def resolve(self, host, port, family):
        return [
            {
                "hostname": host,
                "host": "1.1.1.1",
                "port": port,
                "family": family,
                "proto": 0,
                "flags": 0,
            }
        ]

    monkeypatch.setattr(ThreadedResolver, "resolve", resolve)
    async with route.lifespan() as client:
        results = await client.connector._resolve_host("source.example", 443)
    assert [result["host"] for result in results] == ["1.1.1.1"]


@pytest.mark.asyncio
async def test_resolver_rejects_nonpublic_addresses(monkeypatch):
    async def resolve(self, host, port, family):
        return [
            {
                "hostname": host,
                "host": "127.0.0.1",
                "port": port,
                "family": family,
                "proto": 0,
                "flags": 0,
            }
        ]

    monkeypatch.setattr(ThreadedResolver, "resolve", resolve)
    async with route.lifespan() as client:
        with pytest.raises(OSError):
            await client.connector._resolve_host("source.example", 443)


@pytest.mark.asyncio
async def test_pending_download_keeps_other_requests_responsive(monkeypatch):
    monkeypatch.setenv("RSSERPENT_PROXY_SOURCES", SOURCE)
    entered = asyncio.Event()
    release = asyncio.Event()

    @asynccontextmanager
    async def get(client, url, *, allow_redirects):
        entered.set()
        await release.wait()
        yield SimpleNamespace(
            status=200,
            headers={},
            content_length=None,
            content=SimpleNamespace(iter_chunked=lambda _: chunks(FEED)),
        )

    monkeypatch.setattr(aiohttp.ClientSession, "get", get)
    app = create_app([plugin])
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        fetching = asyncio.create_task(client.get(PATH))
        try:
            await asyncio.wait_for(entered.wait(), timeout=2)
            assert (await asyncio.wait_for(client.get("/"), timeout=2)).status_code == 200
            assert not fetching.done()
        finally:
            release.set()
            response = await fetching
    assert response.status_code == 200
