from urllib.parse import quote

import arrow
from rsserpent_rev.models import Entry, Feed
from rsserpent_rev.utils import cached

from .._http import get_client

path = "/slackware-news"
source = "http://www.slackware.com/"


@cached
async def provider() -> Feed:
    page = await get_client().get_html(source)
    entries = []
    for table in page("center:not(body > center) > table").items():
        rows = table("tr")
        title = rows.eq(0)("b").text()
        if not title:
            continue
        date = rows.eq(1)("td").eq(1)("b").text()
        entries.append(
            Entry(
                id=f"urn:slackware:news:{quote(date or title, safe='')}",
                title=title,
                summary=rows.eq(1)("td").eq(0).text() or None,
                link=source,
                published_at=arrow.get(date, "ddd MMM D HH:mm:ss ZZZ YYYY").datetime
                if date
                else None,
            )
        )
    return Feed(
        title="The Slackware Linux Project",
        link=source,
        description="The Slackware Linux Project News",
        entries=entries,
    )
