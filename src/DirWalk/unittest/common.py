import contextlib

import pytest


class TestCommon:
    # adapted from https://stackoverflow.com/a/42327075
    @contextlib.contextmanager
    def does_not_raise(self, exception):
        try:
            yield
        except exception:
            raise pytest.fail(f'raised unwanted exception {exception}')


    def assert_dirwalk(self, root_path, found_paths, expected_files,
                       ignore_order=False):
        found_files = []

        for file_path in found_paths:
            found_files.append(
                str(file_path.relative_to(root_path)))

        if ignore_order:
            found_files = sorted(found_files)
            expected_files = sorted(expected_files)

        assert found_files == expected_files
