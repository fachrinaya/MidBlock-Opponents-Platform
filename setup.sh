#!/bin/sh
set -eu
cd "$(dirname "$0")"
./tools/python.sh -m venv .venv
if [ -d vendor/wheels ] && [ "$(uname -s)" = Darwin ] && [ "$(uname -m)" = arm64 ]; then
  if ! .venv/bin/python -m pip install --no-index --find-links vendor/wheels -r requirements.lock.txt; then
    .venv/bin/python -m pip install -r requirements.lock.txt
  fi
else
  .venv/bin/python -m pip install -r requirements.lock.txt
fi
.venv/bin/python run.py doctor
echo 'Ready. Run .venv/bin/python run.py demo, or double-click Open Prototype.command.'
