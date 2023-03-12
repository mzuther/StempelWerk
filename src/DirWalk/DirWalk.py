#!/usr/bin/env python3

# ----------------------------------------------------------------------------
#
#  DirWalk
#  =======
#  Custom directory walker
#
#  Copyright (c) 2022-2023 Martin Zuther (https://www.mzuther.de/)
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
#  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
#  COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
#  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
#  OF THE POSSIBILITY OF SUCH DAMAGE.
#
#  Thank you for using free software!
#
# ----------------------------------------------------------------------------

import math
import os
import pathlib
import sys


def dirwalk_recurse(root_directory, directories_first,
                    include_directories, follow_symlinks,
                    included, modified_after):
    directories = []
    files = []

    root_directory = pathlib.Path(root_directory)

    # "os.scandir" minimizes system calls (including the retrieval of
    # timestamps)
    for dir_entry in os.scandir(root_directory):
        current_path = root_directory / dir_entry.name

        # process directories
        if dir_entry.is_dir(follow_symlinks=follow_symlinks):
            is_included = is_directory_included(
                current_path, dir_entry, included, modified_after)

            if is_included:
                directories.append(current_path)
        # process files
        elif dir_entry.is_file(follow_symlinks=follow_symlinks):
            is_included = is_file_included(
                current_path, dir_entry, included, modified_after)

            if is_included:
                files.append(current_path)

    return directories, files


def is_directory_included(current_path, dir_entry, included, modified_after):
    is_included = True

    # exclude directories
    if is_included:
        is_included = current_path.name not in \
            included.get('excluded_directory_names', [])

    return is_included


def is_file_included(current_path, dir_entry, included, modified_after):
    is_included = True

    # exclude files
    if is_included:
        is_included = current_path.name not in \
            included.get('excluded_file_names', [])

    # only include some file suffixes
    if is_included:
        for suffix in included.get('included_suffixes', []):
            if current_path.match(suffix):
                break
        else:
            is_included = False

    # only include files modified after a given date
    if is_included and modified_after:
        # get timestamp of linked file, not of symlink
        stat_result = dir_entry.stat(follow_symlinks=True)

        # "st_mtime_ns" gets the exact timestamp, although
        # nanoseconds may be missing or inexact
        modification_time_in_seconds = stat_result.st_mtime_ns / 1e9

        # round up to ensure that files with inaccurate
        # timestamps and other edge cases are included
        modification_time_in_seconds = math.ceil(
            modification_time_in_seconds)

        is_included = modification_time_in_seconds >= modified_after

    return is_included


def dirwalk(root_directory, directories_first=True, include_directories=False,
            follow_symlinks=False, included=None, modified_after=None):
    if not included:
        included = {}

    # UNIX timestamp, remove digital places after period
    if modified_after:
        modified_after = int(modified_after)

    directories, files = dirwalk_recurse(root_directory, directories_first,
                                         include_directories, follow_symlinks,
                                         included, modified_after)

    # sort results
    directories.sort()
    files.sort()

    # collect results
    result = []

    if not directories_first:
        result.extend(files)

    # recurse
    for current_directory in directories:
        deep_result = dirwalk(current_directory, directories_first,
                              include_directories, follow_symlinks,
                              included, modified_after)

        if include_directories:
            result.append(current_directory + os.sep)

        result.extend(deep_result)

    if directories_first:
        result.extend(files)

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print()
        print('MONSTER:   ME WANT EAT DIRECTORIES.  PLEASE SHOW PLACE.  '
              'THEN ME START EAT.')
        print()
        print('engineer:  please provide the root directory as first '
              'parameter.')
        print()

        exit(1)

    SOURCE_DIR = sys.argv[1]

    INCLUSIONS = {
        'excluded_directory_names': [
        ],
        'excluded_file_names': [
        ],
        'included_suffixes': [
        ],
    }

    MODIFIED_AFTER = None
    # import datetime
    # MODIFIED_AFTER = datetime.datetime(2022, 12, 1).timestamp()

    for current_path_name in dirwalk(
            SOURCE_DIR,
            included=INCLUSIONS,
            modified_after=MODIFIED_AFTER):
        print(current_path_name)
