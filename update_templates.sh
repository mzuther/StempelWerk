#! /usr/bin/bash

# process only templates modified since the last run
uv run stempelwerk --only-modified "./settings_example.json" "$@"
