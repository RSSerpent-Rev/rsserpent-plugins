from rsserpent_rev.utils import HTTPClient, get_plugin_context


def get_client() -> HTTPClient:
    client = get_plugin_context().http
    if client is None:
        message = "This provider requires a plugin HTTP client."
        raise RuntimeError(message)
    return client
