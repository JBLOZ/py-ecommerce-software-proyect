#!/usr/bin/env bash
# scripts/wait-for-it.sh
# Espera a que el host:puerto estén disponibles antes de ejecutar el comando que se pase.

set -e

# Make sure netcat is installed
if ! command -v nc &> /dev/null; then
    echo "Installing netcat..."
    apt-get update && apt-get install -y netcat-openbsd
fi

HOST_PORT=$1
shift

HOST=$(echo "$HOST_PORT" | cut -d':' -f1)
PORT=$(echo "$HOST_PORT" | cut -d':' -f2)
TIMEOUT=15

# Permite pasar un timeout personalizado
while [ "$1" != "--" ] && [ $# -gt 0 ]; do
  case "$1" in
    -t)
      shift
      TIMEOUT=$1
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# Skip past the -- option
if [[ $1 == "--" ]]; then
    shift
fi

echo "Esperando a que $HOST:$PORT esté disponible (timeout ${TIMEOUT}s)..."
echo "Trying to ping $HOST..."
ping -c 1 $HOST || echo "Ping failed, but continuing..."

for ((i=0;i<TIMEOUT;i++)); do
    echo "Attempt $((i+1))/$TIMEOUT: Testing connection to $HOST:$PORT"
    if nc -z "$HOST" "$PORT"; then
      echo "$HOST:$PORT está disponible después de $i segundos."
      echo "Executing command: $@"
      exec "$@"
      exit 0
    fi
    echo "Waiting 1 second before retry..."
    sleep 1
done

echo "Tiempo de espera agotado para $HOST:$PORT"
echo "Network debugging info:"
ip addr
echo "Trying to resolve $HOST:"
getent hosts $HOST || echo "$HOST not found in hosts"
exit 1