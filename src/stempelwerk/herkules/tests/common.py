import contextlib
import difflib
import pathlib
import sys

import pytest


class TestCommon:
    # adapted from https://stackoverflow.com/a/42327075
    @contextlib.contextmanager
    def does_not_raise(self, exception):
        try:
            yield
        except exception:
            raise pytest.fail(f'raised unwanted exception {exception}')


    def assert_herkules(self, root_path, expected_files, actual_paths,
                        ignore_order=False):
        actual_files = []
        for file_path in actual_paths:
            assert isinstance(file_path, pathlib.Path)

            file_path_relative = file_path.relative_to(root_path)
            actual_files.append(str(file_path_relative))

        if ignore_order:
            expected_files = sorted(expected_files)
            actual_files = sorted(actual_files)

        if actual_files != expected_files:
            # force well-formatted diff output
            expected_files = '\n'.join(expected_files) + '\n'
            actual_files = '\n'.join(actual_files) + '\n'

            diff_result = difflib.unified_diff(
                expected_files.splitlines(keepends=True),
                actual_files.splitlines(keepends=True),
                fromfile='EXPECTED',
                tofile='ACTUAL')

            print('------------------------------------------------------')
            print()
            print('Difference between expected and actual output:')
            print()
            sys.stdout.writelines(diff_result)
            print()

            pytest.fail('Found differing files.')
