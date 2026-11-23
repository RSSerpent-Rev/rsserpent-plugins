import hashlib
from urllib.parse import quote

from feedgen.feed import FeedGenerator
from pydantic import BaseModel, Field
from rsserpent_rev.models import FeedResult
from rsserpent_rev.utils import HTTPClient, cached
from starlette.exceptions import HTTPException

from .._http import get_client
from ..admob_sdk_update import route as admob_sdk_update
from ..applovin_sdk_update import route as applovin_sdk_update
from ..csj_sdk_update import route as csj_sdk_update
from .github_release import get_changelog, get_feed

path = "/cocoapods/{pod}"


class Parameters(BaseModel):
    pod: str = Field(min_length=1)


@cached
async def provider(pod: str) -> FeedResult:
    if pod == "AppLovinSDK":
        return await applovin_sdk_update.provider("ios")
    if pod == "Google-Mobile-Ads-SDK":
        return await admob_sdk_update.provider("ios")
    if pod == "Ads-CN-Beta":
        return await csj_sdk_update.provider(197)
    if pod in {".", ".."}:
        raise HTTPException(400, "Invalid pod name")

    return await fetch_changelog(get_client(), pod)


async def fetch_changelog(client: HTTPClient, pod: str) -> FeedGenerator:
    if pod == "Alamofire":
        releases = await get_feed(
            client, "https://github.com/Alamofire/Alamofire/releases.atom"
        )
    else:
        releases = await get_changelog(client, pod)

    if releases is not None:
        releases.title(f"{pod} Changelog")
        return releases
    return await get_specs_log(client, pod)


async def get_specs_log(client: HTTPClient, pod: str) -> FeedGenerator:
    md5 = hashlib.md5(pod.encode()).hexdigest()
    name = quote(pod, safe="")
    url = f"https://github.com/CocoaPods/Specs/commits/master/Specs/{md5[0]}/{md5[1]}/{md5[2]}/{name}.atom"
    fg = await get_feed(client, url)
    if fg is None:
        raise HTTPException(404, "Pod not found. Check the case-sensitive name.")

    changelog_url = {
        "Google-Mobile-Ads-SDK": "https://developers.google.com/admob/ios/rel-notes",
        "AppLovinSDK": "https://developers.applovin.com/en/ios/changelog",
        "Firebase": "https://firebase.google.com/support/release-notes/ios",
        "FacebookSDK": "https://github.com/facebook/facebook-ios-sdk/blob/main/CHANGELOG.md",
        "Ads-CN": "https://www.csjplatform.com/supportcenter/5373",
        "Ads-Gloabl": "https://www.csjplatform.com/supportcenter/5373",
        "AppsFlyerFramework": "https://support.appsflyer.com/hc/en-us/articles/115001224823-AppsFlyer-iOS-SDK-release-notes",
    }

    fg.title(f"{pod} Changelog")

    if pod in changelog_url:
        for entry in fg.entry():
            entry.description(
                f"{entry.description() or ''}\nChangelog: {changelog_url[pod]}"
            )

    return fg
