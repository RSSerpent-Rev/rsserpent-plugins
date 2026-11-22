#!/bin/sh
set -eu

cd "$(dirname "$0")/.."
for member in plugins/*; do
    if [ -d "$member/tests" ]; then
        python -m pytest -q "$member/tests"
    fi
done
