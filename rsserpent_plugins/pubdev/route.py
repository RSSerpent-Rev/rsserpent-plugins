from urllib.parse import urljoin

import arrow
from pydantic import BaseModel, Field
from rsserpent_rev.models import Entry, Feed
from rsserpent_rev.utils import cached

from .._http import get_client

path = "/pubdev/update/{package}"


class Parameters(BaseModel):
    package: str = Field(pattern=r"^[a-z][a-z0-9_]*$")


@cached
async def provider(package: str) -> Feed:
    client = get_client()
    source = f"https://pub.dev/packages/{package}"
    changelog_page = await client.get_html(f"{source}/changelog")
    changelog = {
        entry("h2").text().strip().removesuffix(" #"): entry(
            ".changelog-content"
        ).text()
        for entry in changelog_page(".changelog-entry").items()
    }

    versions_page = await client.get_html(f"{source}/versions")
    entries = []
    for row in versions_page("tbody tr").items():
        cells = row("td")
        if len(cells) < 4:
            continue
        version = cells.eq(0).text()
        href = cells.eq(0)("a").attr("href")
        date = cells.eq(3)("a").attr("data-timestamp")
        entries.append(
            Entry(
                title=f"{package} {version} 更新",
                link=urljoin(source, href) if href else None,
                summary=changelog.get(version) or None,
                published_at=arrow.get(date, "x").datetime if date else None,
            )
        )

    latest = entries[0].published_at if entries else None
    return Feed(
        title=f"{package} 更新日志",
        link=source,
        description=f"最新更新日期：{latest:%Y-%m-%d}" if latest else None,
        published_at=latest,
        entries=entries,
    )
