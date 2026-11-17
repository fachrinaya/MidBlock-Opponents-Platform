#!/bin/sh
# Finder launches can have a different PATH from an interactive Terminal.
set -eu
if [ -n "${PYTHON_BIN:-}" ]; then
  "$PYTHON_BIN" -c 'import sys; assert sys.version_info >= (3,10)'
  exec "$PYTHON_BIN" "$@"
fi
for task_python in python3.11 /opt/homebrew/bin/python3.11 /usr/local/bin/python3.11 python3 python3.12 python3.13 python3.14; do
  if command -v "$task_python" >/dev/null 2>&1 && "$task_python" -c 'import sys; assert sys.version_info >= (3,10)' >/dev/null 2>&1; then
    exec "$task_python" "$@"
  fi
done
echo 'Install Python 3.10 or newer, or set PYTHON_BIN to its executable path.' >&2
exit 1
