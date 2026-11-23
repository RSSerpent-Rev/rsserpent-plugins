import json

import arrow
from pydantic import BaseModel, Field, SecretStr
from rsserpent_rev.models import Entry, Feed
from rsserpent_rev.utils import cached, get_plugin_context
from starlette.exceptions import HTTPException

from .._http import get_client

path = "/csj-sdk-update/{platform:int}"


class Parameters(BaseModel):
    platform: int = Field(gt=0)


class Settings(BaseModel):
    sid_guard: SecretStr | None = None


@cached
async def provider(platform: int) -> Feed:
    """Return the update logs of CSJ SDK."""
    settings = get_plugin_context().settings
    if isinstance(settings, Settings) and settings.sid_guard:
        headers = {"Cookie": f"sid_guard={settings.sid_guard.get_secret_value()}"}
    else:
        headers = None
    response = await get_client().get_json(
        "https://www.csjplatform.com/union_pangle/api/access_document/list?",
        headers=headers,
    )
    logs = next(
        (record for record in response["data"]["list"] if record["Id"] == platform),
        None,
    )
    if logs is None:
        raise HTTPException(404, "SDK platform not found")

    url = f"https://www.csjplatform.com/union/media/union/download/log?id={platform}"
    return Feed(
        title=f"{logs['Name']} 更新日志",
        link=url,
        description=logs["Name"],
        entries=[
            Entry(
                id=f"urn:csj:sdk:{platform}:{log['UpdateVersion']}",
                title=f"{logs['Name']} {log['UpdateVersion']} 更新",
                content=log["UpdateInfo"] or None,
                content_type="html",
                link=url,
                published_at=arrow.get(log["UpdateDate"]).datetime,
            )
            for log in json.loads(logs["Log"])
        ],
    )
