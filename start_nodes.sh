#!/bin/bash

trap '[ ! -z "$(jobs -p)" ] && kill $(jobs -p)' SIGINT SIGTERM EXIT

from="$1"
to="$2"
dim="$3"
t="$4"
prefix="$5"
conf="$6"

for id in $(seq ${from} $((${to} - 1))); do
    python3 -u ${prefix}/main.py ${dim} ${id} ${t} ${conf} &
done
wait
