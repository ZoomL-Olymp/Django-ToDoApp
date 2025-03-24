#!/bin/bash
# wait-for-it.sh

set -e

host_port="$1"  #  <--  Get the combined host:port
shift
cmd="$@"

# Split host:port into separate variables
host=$(echo "$host_port" | cut -d ':' -f 1)  #  <--  Extract host
port=$(echo "$host_port" | cut -d ':' -f 2)  #  <--  Extract port

while ! nc -z "$host" "$port"; do  #  <--  Use separate host and port
  >&2 echo "Waiting for $host:$port to be available..."
  sleep 1
done

>&2 echo "$host:$port is available! Executing command: $cmd"
exec $cmd