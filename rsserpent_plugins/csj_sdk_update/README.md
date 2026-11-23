# rsserpent-plugin-csj-sdk-update

[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![mypy: checked](https://img.shields.io/badge/mypy-checked-blue.svg)](https://github.com/python/mypy)

## Introduction

Set the `sid_guard` field from an environment variable in your instance TOML.

```toml
[plugin_env."rsserpent_plugins.csj_sdk_update"]
sid_guard = "CSJ_SID_GUARD"
```

Set `CSJ_SID_GUARD` to the value of the upstream `sid_guard` cookie and pass the variable to the container. If you use the CocoaPods `Ads-CN-Beta` route, add the same mapping under `[plugin_env."rsserpent_plugins.cocoapods"]`.
