#!/bin/bash

ids="$1"
dim="$2"
timeout="$3"
conf="$4"

parallel --jobs 0 --timeout ${timeout} --header : \
    "sleep 0.5; python3 -u main.py ${dim} {id} ${conf}" ::: id ${ids}
