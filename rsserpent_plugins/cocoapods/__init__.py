from rsserpent_rev.models import FeedRoute, Persona, Plugin
from rsserpent_rev.utils import HTTPClient

from ..csj_sdk_update.route import Settings
from . import route

plugin = Plugin(
    name="rsserpent-plugin-cocoapods",
    author=Persona(
        name="EkkoG",
        link="https://github.com/EkkoG",
        email="beijiu572@gmail.com",
    ),
    prefix="/cocoapods",
    repository="https://github.com/RSSerpent-Rev/rsserpent-plugin-cocoapods",
    routers={route.path: FeedRoute(route.provider, route.Parameters)},
    settings_model=Settings,
    http_client=lambda: HTTPClient(trust_env=False),
    route_docs={
        route.path: {
            "summary": "Releases of a CocoaPods package",
            "parameters": {"pod": "Exact pod name, including its letter case."},
            "examples": [
                {
                    "label": "Google Mobile Ads SDK",
                    "path": {"pod": "Google-Mobile-Ads-SDK"},
                },
            ],
        },
    },
)
