from urllib.parse import urljoin

import arrow
from rsserpent_rev.models import Entry, Feed
from rsserpent_rev.utils import cached

from .._http import get_client

path = "/apple-upcoming-requirements"
source = "https://developer.apple.com/news/upcoming-requirements/"


@cached
async def provider() -> Feed:
    page = await get_client().get_html(source)
    entries = []
    for article in page("section.article-list article").items():
        title = article("a.article-title")
        if not title or not (href := title.attr("href")):
            continue
        date = article("p.article-date").text().partition(" ")[2]
        entries.append(
            Entry(
                title=title.text(),
                link=urljoin(source, href),
                summary=article("span.article-text").text() or None,
                published_at=arrow.get(date, "MMMM D, YYYY").datetime if date else None,
            )
        )
    return Feed(
        title="Apple developer news - Upcoming requirements",
        link=source,
        entries=entries,
    )
