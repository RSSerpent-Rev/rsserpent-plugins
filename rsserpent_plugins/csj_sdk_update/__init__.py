from rsserpent_rev.models import Persona, Plugin

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
    routers={route.path: route.provider},
    route_docs={
        route.path: {
            "summary": "CSJ SDK release notes",
            "description": "The instance operator must set CSJ_SID_GUARD to access the CSJ release notes.",
            "parameters": {"platform": "Numeric SDK release log ID from the CSJ site."},
            "examples": [
                {"label": "Ads-CN Beta", "path": {"platform": "197"}},
            ],
        },
    },
)
