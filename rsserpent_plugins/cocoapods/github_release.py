import asyncio
import re
from io import BytesIO
from urllib.parse import quote, urlsplit

import feedparser
from feedgen.feed import FeedGenerator
from feedparser_to_feedgen import to_feedgen
from lxml import html
from lxml.etree import ParserError, XMLSyntaxError
from rsserpent_rev.utils import HTTPClient
from starlette.exceptions import HTTPException

REPOSITORY = re.compile(r"/([a-zA-Z0-9-]+)/([a-zA-Z0-9_.-]+)/?")


def repository_url(link: str) -> str | None:
    try:
        url = urlsplit(link)
    except ValueError:
        return None
    if (
        url.scheme != "https"
        or url.netloc.lower() != "github.com"
        or url.query
        or url.fragment
    ):
        return None
    match = REPOSITORY.fullmatch(url.path)
    if match is None:
        return None
    owner, repository = match.groups()
    repository = repository.removesuffix(".git")
    if repository in {"", ".", ".."}:
        return None
    return f"https://github.com/{owner}/{repository}"


async def get_feed(client: HTTPClient, url: str) -> FeedGenerator | None:
    response = await client.get(url)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    feed = await asyncio.to_thread(
        feedparser.parse, BytesIO(response.content), response_headers={"content-location": url}
    )
    if not feed.version or not feed.feed.get("title"):
        raise HTTPException(502, "Upstream response is not a feed")
    if not feed.entries:
        return None
    feed.feed["link"] = feed.feed.get("link") or url
    feed.feed["description"] = feed.feed.get("description") or feed.feed.title
    for entry in feed.entries:
        if "summary" not in entry and entry.get("content"):
            entry["summary"] = entry.content[0].value
    try:
        return to_feedgen(feed)
    except (AttributeError, TypeError, ValueError) as exception:
        raise HTTPException(502, "Upstream feed has invalid metadata") from exception


async def get_changelog(client: HTTPClient, pod: str) -> FeedGenerator | None:
    response = await client.get(f"https://cocoapods.org/pods/{quote(pod, safe='')}")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    try:
        tree = html.fromstring(response.content)
    except (ParserError, XMLSyntaxError) as exception:
        raise HTTPException(502, "Upstream response is not a pod page") from exception
    for link in tree.xpath(
        "//ul[contains(concat(' ', normalize-space(@class), ' '), ' links ')]//a/@href"
    ):
        repository = repository_url(link)
        if repository is not None:
            return await get_feed(client, repository + "/releases.atom")
    return None
