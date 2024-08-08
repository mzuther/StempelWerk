#!/usr/bin/env python3

# %% Imports
import datetime
import pathlib

from dirwalk.DirWalk import dirwalk


# %% Initialization
# directory to be crawled (can also be a string)
ROOT_DIRECTORY = pathlib.Path('.')

# optional: return directories and their contents before regular files
DIRECTORIES_FIRST = True

# optional: whether subdirectories should be included in the output; their
# contents will always be crawled, however, regardless of this setting
INCLUDE_DIRECTORIES = False

# optional: include files and directories which are symlinks
FOLLOW_SYMLINKS = False

# globs: https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.match
SELECTOR = {
    # optional: directories that should not be crawled (full name is matched)
    'excluded_directory_names': [
        '.git',
    ],
    # optional: file names that should be included in the result (glob)
    'excluded_file_names': [
        '*.*c',
    ],
    # optional: file names that should be excluded from the result (glob,
    # "*" by default)
    'included_file_names': [
    ],
}

# optional: only include directories and files with were modified at or past
# the given time; for symlinks, this checks the original file
MODIFIED_SINCE = datetime.datetime(2024, 8, 1, 8, 30, 0)


# %% Crawl directory & display results
contents = dirwalk(
    ROOT_DIRECTORY, DIRECTORIES_FIRST, INCLUDE_DIRECTORIES,
    FOLLOW_SYMLINKS, SELECTOR, MODIFIED_SINCE)

print()
for entry in contents:
    print(f'* { entry }')
print()
