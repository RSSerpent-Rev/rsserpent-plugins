# rsserpent-plugin-rss-proxy

[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![mypy: checked](https://img.shields.io/badge/mypy-checked-blue.svg)](https://github.com/python/mypy)
# Allowed sources

Set `RSSERPENT_PROXY_SOURCES` to the exact HTTPS feed URLs that you want to serve, one URL per line.
The proxy is disabled when this list is empty. It rejects redirects and connections to non-public addresses.
The download limit is 2 MiB and the total download timeout is 10 seconds.

Put the full feed URL after `/proxy/`. Encode any query in the source URL as part of the path.
For example, `/proxy/https://example.org/feed.rss%3Fedition%3Dlocal?format=atom` selects Atom output.
Without `format`, the route returns RSS.
