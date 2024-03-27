#!/bin/bash

exec 3<>/dev/tcp/localhost/"$1"

echo -e "GET /healthy HTTP/1.1\n\n" >&3

timeout 1 cat <&3 | grep OK || exit 1