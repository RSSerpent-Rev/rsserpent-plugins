# RSSerpent official plugins

One Python package provides all ten official RSSerpent plugins. Each subpackage of `rsserpent_plugins` exports a `plugin` object. See [Sources](SOURCES.md) for the original repositories and licenses.

## Install and enable plugins

Use CPython 3.14 or 3.15 and RSSerpent 0.3 or later with the module configuration loader. Install the official plugin wheel in the same environment as the core:

```sh
uv pip install /path/to/rsserpent_plugins-0.3.0-py3-none-any.whl
```

To install from Git, use a full commit that contains the aggregate package:

```sh
uv pip install 'rsserpent-plugins @ git+https://github.com/RSSerpent-Rev/rsserpent-plugins.git@<commit>'
```

List the plugins to enable in `rsserpent.toml`:

```toml
plugins = ["rsserpent_plugins.bilibili"]
```

Start RSSerpent with that configuration:

```sh
RSSERPENT_CONFIG=rsserpent.toml uv run --no-sync uvicorn rsserpent_rev:app
```

| Plugin | Python module |
| --- | --- |
| AdMob SDK Update | `rsserpent_plugins.admob_sdk_update` |
| Apple Newsroom | `rsserpent_plugins.apple_newsroom` |
| Apple Upcoming Requirements | `rsserpent_plugins.apple_upcoming_requirements` |
| AppLovin SDK Update | `rsserpent_plugins.applovin_sdk_update` |
| Bilibili | `rsserpent_plugins.bilibili` |
| CocoaPods | `rsserpent_plugins.cocoapods` |
| CSJ SDK Update | `rsserpent_plugins.csj_sdk_update` |
| PubDev | `rsserpent_plugins.pubdev` |
| RSS Proxy | `rsserpent_plugins.rss_proxy` |
| Slackware News | `rsserpent_plugins.slackware_news` |

CocoaPods uses the three SDK providers for its own feeds. To enable the SDKs' separate subscriptions, also list their modules. RSS Proxy also requires `RSSERPENT_PROXY_SOURCES`. See [RSS Proxy configuration](rsserpent_plugins/rss_proxy/README.md).

You can install independently published Python plugins from wheels, Git or PyPI. Add each plugin's importable module name to the same list. The module must export a `plugin` instance of `rsserpent_rev.models.Plugin`.

## Develop and test

```sh
uv sync --locked
uv run --no-sync pytest
uv build
```

The lock pins a public core commit for the provider API tests. To test the app with module configuration, install the built plugin wheel in an environment with RSSerpent 0.3. See the [RSSerpent deployment guide](https://github.com/RSSerpent-Rev/RSSerpent/blob/main/docs/deployment/plugin.md).
