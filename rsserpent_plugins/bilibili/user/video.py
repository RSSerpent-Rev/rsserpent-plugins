from datetime import UTC, datetime

from pydantic import BaseModel, Field
from rsserpent_rev.models import Entry, Feed
from rsserpent_rev.utils import cached

from ..._http import get_client

path = "/bilibili/user/{uid}/video"


class Parameters(BaseModel):
    uid: int = Field(gt=0)


@cached
async def provider(uid: int) -> Feed:
    """订阅 up 上传的最新视频."""
    client = get_client()
    user_info = await client.get_json(
        "https://api.bilibili.com/x/space/acc/info",
        params={"mid": uid, "jsonp": "jsonp"},
    )
    video_list = await client.get_json(
        "https://api.bilibili.com/x/space/arc/search",
        params={
            "mid": uid,
            "ps": 30,
            "tid": 0,
            "pn": 1,
            "keyword": "",
            "order": "pubdate",
            "jsonp": "jsonp",
        },
    )
    if user_info["code"] != 0:
        raise ValueError(user_info["message"])
    if video_list["code"] != 0:
        raise ValueError(video_list["message"])
    username = user_info["data"]["name"]

    return Feed(
        title=f"{username}的最新投稿视频",
        link=f"https://space.bilibili.com/{uid}/video",
        description=user_info["data"]["sign"] or None,
        entries=[
            Entry(
                title=item["title"],
                summary=item["description"] or None,
                link=f"https://www.bilibili.com/video/{item['bvid']}",
                published_at=datetime.fromtimestamp(item["created"], UTC),
                author=username,
            )
            for item in video_list["data"]["list"]["vlist"]
        ],
    )
