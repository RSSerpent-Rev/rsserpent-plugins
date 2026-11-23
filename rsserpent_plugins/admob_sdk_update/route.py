from datetime import datetime
from typing import Annotated, Literal

import arrow
from lxml import html
from pydantic import BaseModel, BeforeValidator
from rsserpent_rev.models import Entry, Feed
from rsserpent_rev.utils import cached

from .._http import get_client

path = "/admob/sdk-update/{platform}"
platform_names = {"ios": "iOS", "android": "Android", "cpp": "C++"}


class Parameters(BaseModel):
    platform: Annotated[Literal["ios", "android", "cpp"], BeforeValidator(str.lower)]


def release_date(value: str) -> datetime | None:
    for fmt in ("YYYY-MM-DD", "YYYY-M-DD", "MMMM D, YYYY", "YYYY‑MM‑DD"):
        try:
            return arrow.get(value.strip(), fmt).datetime
        except arrow.parser.ParserError:
            continue
    return None


@cached
async def provider(platform: str) -> Feed:
    url = f"https://developers.google.com/admob/{platform}/rel-notes"
    page = await get_client().get_html(url)
    label = platform_names[platform]
    entries = []
    for row in page("table").eq(0).find("tr").items():
        cells = row("td")
        if len(cells) < 3:
            continue
        version = cells.eq(0).text()
        entries.append(
            Entry(
                id=f"urn:admob:sdk:{platform}:{version}",
                title=f"AdMob SDK {label} {version} Update",
                content=html.tostring(cells[2], encoding="unicode"),
                content_type="html",
                link=url,
                published_at=release_date(cells.eq(1).text()),
            )
        )
    return Feed(
        title=f"AdMob SDK {label} Update",
        link=url,
        description="Latest AdMob SDK update.",
        published_at=entries[0].published_at if entries else None,
        entries=entries,
    )
