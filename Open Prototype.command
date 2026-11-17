#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ -x .venv/bin/python ]; then
  exec .venv/bin/python run.py serve --port 4182 --open
fi
exec ./tools/python.sh run.py serve --port 4182 --open
