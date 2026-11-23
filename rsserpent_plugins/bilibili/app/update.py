from datetime import UTC, datetime
from typing import Literal
from urllib.parse import quote

from pydantic import BaseModel
from rsserpent_rev.models import Entry, Feed
from rsserpent_rev.utils import cached

from ..._http import get_client

platform_trans = {
    "android": "安卓版",
    "iphone": "iPhone 版",
    "ipad": "iPad HD 版",
    "win": "UWP 版",
    "android_tv_yst": "TV 版",
}
path = "/bilibili/app/update/{platform}"


class Parameters(BaseModel):
    platform: Literal["android", "iphone", "ipad", "win", "android_tv_yst"]


@cached
async def provider(platform: str) -> Feed:
    """订阅 Bilibili 客户端更新信息."""
    source = "https://app.bilibili.com"
    updates = await get_client().get_json(
        f"{source}/x/v2/version", params={"mobi_app": platform}
    )
    return Feed(
        title=f"哔哩哔哩更新情报 - {platform_trans[platform]}",
        link=source,
        id=f"urn:bilibili:app:{platform}",
        entries=[
            Entry(
                id=f"urn:bilibili:app:{platform}:{quote(item['version'], safe='')}",
                title=item["version"],
                summary=item["desc"] or None,
                link=source,
                published_at=datetime.fromtimestamp(item["ptime"], UTC),
            )
            for item in updates["data"]
        ],
    )
