from urllib.parse import urljoin

import arrow
from rsserpent_rev.models import Entry, Feed
from rsserpent_rev.utils import cached

from .._http import get_client

path = "/apple-newsroom"
newsroom = "https://www.apple.com.cn/newsroom/"


@cached
async def provider() -> Feed:
    archive = await get_client().get_json(newsroom + "archive.json")
    return Feed(
        title="Apple Newsroom",
        link=newsroom,
        entries=[
            Entry(
                id=urljoin(newsroom, item["link"]),
                title=item["title"],
                link=urljoin(newsroom, item["link"]),
                content=item["description"] or None,
                content_type="html",
                published_at=arrow.get(item["date"], "YYYY 年 M 月 D 日").datetime,
                categories=[item["category"]["text"]],
            )
            for item in archive["results"][0]["result"]
        ],
    )
