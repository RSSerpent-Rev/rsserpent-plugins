import asyncio
import ipaddress
import os
import socket
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from io import BytesIO

import aiohttp
import feedparser
from aiohttp.abc import ResolveResult
from aiohttp.resolver import ThreadedResolver
from feedparser_to_feedgen import to_feedgen  # type: ignore[import-not-found]
from rsserpent_rev.models import Feed
from rsserpent_rev.utils import cached
from rsserpent_rev.utils import provider as provider_utils
from starlette.exceptions import HTTPException
from yarl import URL

path = "/proxy/{url:path}"
MAX_FEED_BYTES = 2 * 1024 * 1024


def sources() -> set[str]:
    return {line.strip() for line in os.getenv("RSSERPENT_PROXY_SOURCES", "").splitlines() if line.strip()}


def enabled() -> bool:
    return bool(sources())


def public_ip(host: str) -> bool:
    address = ipaddress.ip_address(host)
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        address = address.ipv4_mapped
    if isinstance(address, ipaddress.IPv6Address) and (address.is_site_local or address.scope_id):
        return False
    return address.is_global and not (address.is_multicast or address.is_reserved)


class PublicResolver(ThreadedResolver):
    async def resolve(
        self, host: str, port: int = 0, family: socket.AddressFamily = socket.AF_INET
    ) -> list[ResolveResult]:
        results = await super().resolve(host, port, family)
        if not results or any(not public_ip(result["host"]) for result in results):
            raise OSError("Upstream did not resolve to public addresses")
        return results


def allowed_url(raw_url: str) -> URL:
    if raw_url not in sources():
        raise HTTPException(403, "Feed source is not allowed")
    try:
        url = URL(raw_url)
        host = url.raw_host
        if url.scheme != "https" or not host or url.raw_user is not None or url.fragment:
            raise HTTPException(403, "Feed source is not allowed")
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass
        else:
            if not public_ip(host):
                raise HTTPException(403, "Feed source is not allowed")
    except ValueError as exception:
        raise HTTPException(403, "Feed source is not allowed") from exception
    return url


@asynccontextmanager
async def lifespan() -> AsyncIterator[aiohttp.ClientSession]:
    resolver = PublicResolver()
    try:
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(resolver=resolver),
            timeout=aiohttp.ClientTimeout(total=10),
            cookie_jar=aiohttp.DummyCookieJar(),
            trust_env=False,
            auto_decompress=False,
            headers={"Accept-Encoding": "identity"},
        ) as session:
            yield session
    finally:
        await resolver.close()


async def download(session: aiohttp.ClientSession, url: URL) -> bytes:
    try:
        async with session.get(url, allow_redirects=False) as response:
            if response.status != 200 or response.headers.get("Content-Encoding", "identity").lower() != "identity":
                raise HTTPException(502, "Bad Gateway")
            if response.content_length is not None and response.content_length > MAX_FEED_BYTES:
                raise HTTPException(502, "Upstream feed is too large")
            body = bytearray()
            async for chunk in response.content.iter_chunked(65536):
                if len(body) + len(chunk) > MAX_FEED_BYTES:
                    raise HTTPException(502, "Upstream feed is too large")
                body.extend(chunk)
            return bytes(body)
    except (TimeoutError, asyncio.TimeoutError) as exception:
        raise HTTPException(504, "Gateway Timeout") from exception
    except aiohttp.ClientError as exception:
        raise HTTPException(502, "Bad Gateway") from exception


@cached
async def fetch(url: URL) -> Feed:
    resource = getattr(provider_utils, "provider_resource", None)
    session = resource.get() if resource is not None else None
    if isinstance(session, aiohttp.ClientSession):
        body = await download(session, url)
    else:
        async with lifespan() as session:
            body = await download(session, url)

    feed = await asyncio.to_thread(feedparser.parse, BytesIO(body), response_headers={"content-location": str(url)})
    if not feed.version or not feed.feed.get("title"):
        raise HTTPException(502, "Upstream response is not a feed")
    feed.feed["link"] = feed.feed.get("link") or str(url)
    feed.feed["description"] = feed.feed.get("description") or feed.feed.title
    try:
        return to_feedgen(feed)
    except (AttributeError, TypeError, ValueError) as exception:
        raise HTTPException(502, "Upstream feed has invalid metadata") from exception


async def provider(url: str) -> Feed:
    """Fetch an RSS or Atom feed from an allowed source."""
    return await fetch(allowed_url(url))
