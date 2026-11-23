import asyncio
import re
from urllib.parse import quote, urlsplit

import httpx
from feedgen.feed import FeedGenerator
from rsserpent_rev.utils import HTTPClient, parse_feed

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
        parse_feed, response.content, base_url=str(response.url)
    )
    return feed if feed.entry() else None


async def get_changelog(client: HTTPClient, pod: str) -> FeedGenerator | None:
    url = f"https://cocoapods.org/pods/{quote(pod, safe='')}"
    try:
        page = await client.get_html(url)
    except httpx.HTTPStatusError as exception:
        if exception.response.status_code == 404:
            return None
        raise
    for link in page("ul.links a[href]").items():
        repository = repository_url(link.attr("href"))
        if repository is not None:
            return await get_feed(client, repository + "/releases.atom")
    return None
