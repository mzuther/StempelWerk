#! /usr/bin/bash

# process only templates modified since the last run
python3 -m src.StempelWerk --only-modified "../settings_example.json"
