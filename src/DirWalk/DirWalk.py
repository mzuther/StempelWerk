#!/usr/bin/env python3

import math
import os
import sys


def dirwalk_recurse(root_directory, directories_first, include_directories,
                    follow_symlinks, included, modified_after):
    root_name = os.fsdecode(root_directory)

    directories = []
    files = []

    # "os.scandir" minimizes system calls (including the retrieval of timestamps)
    with os.scandir(root_directory) as paths_in_directory:
        for current_path in paths_in_directory:
            path_name = os.fsdecode(current_path.name)
            path_relname = os.path.normpath(os.path.join(root_name, path_name))
            path_basename = os.path.basename(path_relname)

            # process directories
            if current_path.is_dir(follow_symlinks=follow_symlinks):
                is_included = True

                # exclude directories
                if included.get('excluded_directory_names', []):
                    is_included = is_included and \
                        path_basename not in included['excluded_directory_names']

                if is_included:
                    directories.append(path_relname)
            # process files
            elif current_path.is_file(follow_symlinks=follow_symlinks):
                is_included = True

                # exclude files
                if included.get('excluded_file_names', []):
                    is_included = is_included and \
                        path_basename not in included['excluded_file_names']

                # only include some file extensions
                if included.get('included_file_extensions', []):
                    _, file_extension = os.path.splitext(path_relname)
                    is_included = is_included and \
                        file_extension in included['included_file_extensions']

                # only include files modified after a given date
                if modified_after:
                    # get timestamp of linked file, not of symlink
                    stat_result = current_path.stat(follow_symlinks=True)

                    # according to the Python documentation, "st_mtime_ns" gets
                    # the exact timestamp, although nanoseconds may be missing
                    # or inexact; round up to ensure that files with inaccurate
                    # timestamps and other edge cases are included
                    modification_time_in_seconds = math.ceil(
                        stat_result.st_mtime_ns / 1e9)

                    is_included = is_included and \
                        modification_time_in_seconds >= modified_after

                if is_included:
                    files.append(path_relname)

    return directories, files


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
        print('MONSTER:   ME WANT EAT DIRECTORIES.  PLEASE SHOW PLACE.  THEN ME START EAT.')
        print()
        print('engineer:  please provide the root directory as first parameter.')
        print()

        exit(1)

    SOURCE_DIR = sys.argv[1]

    # do not end entries with path separators ("/" or "\")!
    INCLUSIONS = {
        'excluded_directory_names': [
        ],
        'excluded_file_names': [
        ],
        'included_file_extensions': [
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
