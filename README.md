# RSSerpent official plugins

The RSSerpent-Rev organization maintains these ten plugins in one uv workspace. Each directory in `plugins/` builds a separate package with its original distribution name, Python module, and subscription routes. See [Sources](SOURCES.md) for the original commits and licenses.

## Install a plugin

Use uv 0.13.9 and CPython 3.14 or 3.15. Install the core and the plugin in the same environment. Replace `<commit>` with the full commit of the published plugin repository.

```sh
uv venv --python 3.14
uv pip install 'rsserpent-rev @ git+https://github.com/RSSerpent-Rev/RSSerpent.git@1da58cea79344b2c1ad881c117d0587dd1e04169' uvicorn \
  'rsserpent-plugin-bilibili @ git+https://github.com/RSSerpent-Rev/rsserpent-plugins.git@<commit>#subdirectory=plugins/bilibili'
.venv/bin/uvicorn rsserpent_rev:app
```

For CocoaPods, use `rsserpent-plugin-cocoapods` and `plugins/cocoapods`. uv installs AdMob, AppLovin, and CSJ from the same commit. To install the CocoaPods wheel, give uv the matching core and SDK wheels with `--find-links`. Update a Git installation by replacing the old commit in your requirements and rebuilding or resyncing the environment.

The core reads the installed `rsserpent.plugin` entry points when it creates the app. This also lets it load independent plugins such as CAA, Douban, Manhuagui, and Zhubai. The RSS Proxy requires explicit sources in `RSSERPENT_PROXY_SOURCES`. See its [configuration](plugins/rss-proxy/README.md).

## Develop and test

Sync all ten packages with the checked-in lock and run the workspace tests and builds:

```sh
uv sync --locked --all-packages
uv run --no-sync sh scripts/test.sh
uv build --all-packages
```

The test script starts a separate pytest process for each plugin. The default tests use fixed responses and can run without contacting the upstream services.

To update the core, change its full commit in `[tool.uv.sources]` and in the install example. Run `uv lock` and run the test commands on both supported Python versions before you commit the lock.
