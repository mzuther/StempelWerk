#! /usr/bin/bash

# process only templates modified since the last run
python3 "./src/StempelWerk.py" --only-modified ../settings_example.json
