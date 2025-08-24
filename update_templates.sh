#! /usr/bin/bash

# process only templates modified since the last run
./stempelwerk.sh --only-modified "./config_example.json" "$@"
