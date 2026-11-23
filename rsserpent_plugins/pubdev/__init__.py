from rsserpent_rev.models import FeedRoute, Persona, Plugin

from . import route

plugin = Plugin(
    name="rsserpent-plugin-pubdev",
    author=Persona(
        name="Ekko",
        link="https://github.com/EkkoG",
        email="beijiu572@gmail.com",
    ),
    prefix="/pubdev/update",
    repository="https://github.com/RSSerpent-Rev/rsserpent-plugin-pubdev",
    routers={
        route.path: FeedRoute(route.provider, route.Parameters),
    },
    http_client=True,
    route_docs={
        route.path: {
            "summary": "Versions of a pub.dev package",
            "parameters": {"package": "Package name from its pub.dev page."},
            "examples": [
                {"label": "http package", "path": {"package": "http"}},
            ],
        },
    },
)
