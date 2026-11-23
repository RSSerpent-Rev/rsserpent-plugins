from rsserpent_rev.models import FeedRoute, Persona, Plugin

from . import route

plugin = Plugin(
    name="rsserpent-plugin-admob-sdk-update",
    author=Persona(
        name="EkkoG",
        link="https://github.com/RSSerpent-Rev",
        email="beijiu572@gmail.com",
    ),
    prefix="/admob/sdk-update",
    repository="https://github.com/RSSerpent-Rev/rsserpent-plugin-admob-sdk-update",
    routers={route.path: FeedRoute(route.provider, route.Parameters)},
    http_client=True,
    route_docs={
        route.path: {
            "summary": "AdMob SDK release notes",
            "parameters": {"platform": "SDK platform: ios, android or cpp."},
            "examples": [
                {"label": "iOS", "path": {"platform": "ios"}},
                {"label": "Android", "path": {"platform": "android"}},
            ],
        },
    },
)
