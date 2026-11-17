#!/bin/sh
# Export these variables yourself; this helper never reads or prints a password.
set -eu
task_key="${SSH_KEY_FILE:-$HOME/.ssh/id_ed25519}"
case "$task_key" in '~/'*) task_key="$HOME/${task_key#\~/}" ;; esac
exec ssh -N -o ExitOnForwardFailure=yes -o IdentitiesOnly=yes \
  -i "$task_key" \
  -L "${LOCAL_DB_PORT:-5433}:127.0.0.1:${REMOTE_DB_PORT:-5432}" \
  "${SSH_USER:-ubuntu}@${SSH_HOST:?Set SSH_HOST to your approved server address}"
