from contextlib import asynccontextmanager

import httpx
import pytest
from rsserpent_rev.main import create_app


@pytest.fixture
def asgi_client():
    @asynccontextmanager
    async def connect(plugin):
        app = create_app([plugin])
        async with app.router.lifespan_context(app) as state:

            async def request_app(scope, receive, send):
                await app(dict(scope, state=state), receive, send)

            transport = httpx.ASGITransport(app=request_app)
            async with httpx.AsyncClient(
                transport=transport, base_url="http://test"
            ) as client:
                yield client

    return connect
