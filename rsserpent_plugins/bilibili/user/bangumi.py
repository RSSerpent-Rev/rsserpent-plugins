from urllib.parse import quote

import arrow
from rsserpent_rev.models import Entry, Feed
from rsserpent_rev.utils import cached

from ..._http import get_client

path = "/bilibili/user/{uid}/bangumi"


@cached
async def provider(uid: int) -> Feed:
    """订阅用户追番列表."""
    return await provider_base(uid, 1, "bangumi", "追番")


async def provider_base(uid: int, series_type: int, kind: str, display: str) -> Feed:
    client = get_client()
    user_info = await client.get_json(
        "https://api.bilibili.com/x/space/acc/info",
        params={"mid": uid, "jsonp": "jsonp"},
    )
    bangumi_list = await client.get_json(
        "https://api.bilibili.com/x/space/bangumi/follow/list",
        params={
            "type": series_type,
            "follow_status": 0,
            "pn": 1,
            "ps": 30,
            "vmid": uid,
        },
    )
    if user_info["code"] != 0:
        raise ValueError(user_info["message"])
    if bangumi_list["code"] != 0:
        raise ValueError(bangumi_list["message"])

    entries = []
    for item in bangumi_list["data"]["list"]:
        if not (episode := item["new_ep"]):
            continue
        label = episode["index_show"]
        identity = quote(str(episode.get("id") or label), safe="")
        date = episode.get("pub_time") or (item.get("publish") or {}).get("pub_time")
        entries.append(
            Entry(
                id=f"urn:bilibili:season:{item['season_id']}:{identity}",
                title=f"{label} - {item['title']}",
                summary=item["evaluate"] or None,
                link=f"https://www.bilibili.com/bangumi/play/ss{item['season_id']}",
                published_at=arrow.get(date).datetime if date else None,
            )
        )
    return Feed(
        title=f"{user_info['data']['name']} 的{display}列表",
        link=f"https://space.bilibili.com/{uid}/{kind}",
        description=user_info["data"]["sign"] or None,
        entries=entries,
    )
