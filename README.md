# RSSerpent official plugins

One Python package provides all ten official RSSerpent plugins. Each subpackage of `rsserpent_plugins` exports a `plugin` object. See [Sources](SOURCES.md) for the original repositories and licenses.

## Deploy

Use the [RSSerpent Docker guide](https://github.com/RSSerpent-Rev/RSSerpent/blob/main/docs/deployment/plugin.md) to run the official image with a TOML file. Add the official package requirement and select the modules you need.

```toml
plugin_requirements = [
  "rsserpent-plugins @ git+https://github.com/RSSerpent-Rev/rsserpent-plugins.git@PLUGIN_COMMIT",
]
plugins = ["rsserpent_plugins.bilibili"]
```

Replace `PLUGIN_COMMIT` with the full commit SHA of the plugin version you want to install. The plugins use the typed provider API from RSSerpent 0.3. Feed readers may show some older entries again after the upgrade. Apple Newsroom now uses absolute article URLs for entry IDs.

## Official modules

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

CocoaPods uses the three SDK providers for its own feeds. To enable the SDKs' separate subscriptions, also list their modules. CSJ uses a [plugin setting for its session cookie](rsserpent_plugins/csj_sdk_update/README.md). RSS Proxy also requires `RSSERPENT_PROXY_SOURCES`. See [RSS Proxy configuration](rsserpent_plugins/rss_proxy/README.md).

You can install independently published Python plugins from wheels, Git or PyPI. Add each plugin's importable module name to the same list. The module must export a `plugin` instance of `rsserpent_rev.models.Plugin`.

## Develop and test

```sh
uv sync --locked
uv run --no-sync pytest
uv build
```

The lock pins the core commit for the provider API tests. To test the app with module configuration, install the built plugin wheel in an environment with RSSerpent 0.3. See the [RSSerpent deployment guide](https://github.com/RSSerpent-Rev/RSSerpent/blob/main/docs/deployment/plugin.md).
