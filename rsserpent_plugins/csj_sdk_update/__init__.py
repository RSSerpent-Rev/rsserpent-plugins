from rsserpent_rev.models import FeedRoute, Persona, Plugin

from . import route

plugin = Plugin(
    name="rsserpent-plugin-csj-sdk-update",
    author=Persona(
        name="EkkoG",
        link="https://github.com/EkkoG",
        email="beijiu572@gmail.com",
    ),
    prefix="/csj-sdk-update",
    repository="https://github.com/rsserpent-rev/rsserpent-plugin-csj-sdk-update",
    routers={route.path: FeedRoute(route.provider, route.Parameters)},
    http_client=True,
    settings_model=route.Settings,
    route_docs={
        route.path: {
            "summary": "CSJ SDK release notes",
            "description": "The instance can configure the CSJ session cookie to access the release notes.",
            "parameters": {"platform": "Numeric SDK release log ID from the CSJ site."},
            "examples": [
                {"label": "Ads-CN Beta", "path": {"platform": "197"}},
            ],
        },
    },
)
