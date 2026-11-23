from rsserpent_rev.models import Feed
from rsserpent_rev.utils import cached

from .bangumi import provider_base

path = "/bilibili/user/{uid}/cinema"


@cached
async def provider(uid: int) -> Feed:
    """订阅用户追剧列表."""
    return await provider_base(uid, 2, "cinema", "追剧")
