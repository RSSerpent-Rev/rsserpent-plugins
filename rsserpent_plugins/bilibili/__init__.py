from rsserpent_rev.models import Persona, Plugin

from . import app, user

plugin = Plugin(
    name="rsserpent-plugin-bilibili",
    author=Persona(
        name="creedowl",
        link="https://github.com/creedowl",
        email="creedowl@gmail.com",
    ),
    prefix="/bilibili",
    repository="https://github.com/RSSerpent-Rev/rsserpent-plugin-bilibili",
    routers={
        user.video.path: user.video.provider,
        user.bangumi.path: user.bangumi.provider,
        user.cinema.path: user.cinema.provider,
        app.update.path: app.update.provider,
    },
    route_docs={
        user.video.path: {
            "summary": "Videos from a Bilibili user",
            "parameters": {"uid": "Numeric user ID from the Bilibili profile URL."},
            "examples": [
                {"label": "Example user", "path": {"uid": "297786973"}},
            ],
        },
        user.bangumi.path: {
            "summary": "Bilibili series followed by a user",
            "parameters": {"uid": "Numeric user ID from the Bilibili profile URL."},
        },
        user.cinema.path: {
            "summary": "Bilibili shows followed by a user",
            "parameters": {"uid": "Numeric user ID from the Bilibili profile URL."},
        },
        app.update.path: {
            "summary": "Bilibili app releases",
            "parameters": {"platform": "Bilibili app platform code, such as android."},
            "examples": [
                {"label": "Android app", "path": {"platform": "android"}},
            ],
        },
    },
)
