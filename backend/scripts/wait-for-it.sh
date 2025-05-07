#!/usr/bin/env bash
# Minimal wait-for-it implementation
if [ $# -lt 2 ]; then
  echo "Usage: $0 host:port -- command"
  exit 1
fi
address="$1"
shift

echo "Waiting for ${address} to be available..."
IFS=':' read -r host port <<< "$address"
while ! nc -z "$host" "$port"; do
  sleep 1
done

echo "${host}:${port} is available, executing command"
exec "$@"