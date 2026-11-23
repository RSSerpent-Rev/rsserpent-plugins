from typing import Annotated, Literal

import arrow
from pydantic import BaseModel, BeforeValidator
from rsserpent_rev.models import Entry, Feed
from rsserpent_rev.utils import cached

from .._http import get_client

path = "/applovin/sdk-update/{platform}"
platform_names = {
    "ios": "iOS",
    "android": "Android",
    "unity": "Unity",
    "react-native": "React Native",
    "flutter": "Flutter",
    "godot": "Godot",
}


class Parameters(BaseModel):
    platform: Annotated[
        Literal["ios", "android", "unity", "react-native", "flutter", "godot"],
        BeforeValidator(str.lower),
    ]


@cached
async def provider(platform: str) -> Feed:
    platform_in_url = platform.replace("-", "_")
    url = f"https://docs.applovin.com/max/api/1.0/changelog/{platform_in_url}"
    updates = await get_client().get_json(url)
    entries = [
        Entry(
            id=f"urn:applovin:sdk:{platform}:{item['version']}",
            title=f"AppLovin Max {platform_names[platform]} SDK {item['version']} 更新",
            content=item["content"] or None,
            content_type="html",
            link=f"https://developers.applovin.com/en/{platform}/changelog",
            published_at=arrow.get(item["published_at"], "MMMM D, YYYY").datetime,
        )
        for item in updates
    ]
    latest = entries[0].published_at if entries else None
    return Feed(
        title=f"AppLovin Max {platform_names[platform]} SDK 更新日志",
        link=url,
        description=f"最新更新日期：{latest:%Y-%m-%d}" if latest else None,
        published_at=latest,
        entries=entries,
    )
