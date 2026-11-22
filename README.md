# RSSerpent official plugins

The RSSerpent-Rev organization maintains these ten plugins in one uv workspace. Each directory in `plugins/` builds a separate package with its original distribution name, Python module, and subscription routes. See [Sources](SOURCES.md) for the original commits and licenses.

## Install a plugin

Use uv 0.13.9 and CPython 3.14 or 3.15. Install a compatible RSSerpent core (0.2.x) and the plugin in the same environment. Replace `<commit>` with the full commit of the published plugin repository.

```sh
uv venv --python 3.14
uv pip install 'rsserpent-rev==0.2.0' uvicorn \
  'rsserpent-plugin-bilibili @ git+https://github.com/RSSerpent-Rev/rsserpent-plugins.git@<commit>#subdirectory=plugins/bilibili'
.venv/bin/uvicorn rsserpent_rev:app
```

For CocoaPods, use `rsserpent-plugin-cocoapods` and `plugins/cocoapods`. uv installs AdMob, AppLovin, and CSJ from the same commit. To install the CocoaPods wheel, give uv the matching core and SDK wheels with `--find-links`. Update a Git installation by replacing the old commit in your requirements and rebuilding or resyncing the environment.

The core reads the installed `rsserpent.plugin` entry points when it creates the app. This also lets it load independent plugins such as CAA, Douban, Manhuagui, and Zhubai. The RSS Proxy requires explicit sources in `RSSERPENT_PROXY_SOURCES`. See its [configuration](plugins/rss-proxy/README.md).

## Develop and test

With a published compatible core and the workspace lock available:

```sh
uv sync --locked --all-packages
uv run --no-sync sh scripts/test.sh
uv build --all-packages
```

The test script starts a separate pytest process for each plugin. The default tests use fixed responses and can run without contacting the upstream services.

Before the compatible core is published, build its wheel in the core checkout with `uv build --wheel`. In a temporary copy of this workspace, add the following entry under the existing `[tool.uv.sources]` table, point it at the built wheel, and run `uv lock` before running the commands above.

```toml
rsserpent-rev = { path = "/absolute/path/to/rsserpent_rev-0.2.0-py3-none-any.whl" }
```

For the shared lock, resolve the core from its published release or specify a full publicly available core commit with `git` and `rev` in `[tool.uv.sources]`. Run `uv lock`, then run the test commands on both supported Python versions before committing the lock.
