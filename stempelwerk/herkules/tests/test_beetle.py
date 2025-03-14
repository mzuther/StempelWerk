# The story, all names, characters, and incidents portrayed in this test are
# fictitious. No identification with actual persons (living or deceased),
# places, buildings, and products is intended or should be inferred.
#
# In other words: I have great and helpful colleagues with a lot of humour. In
# order to make writing these tests more fun, I have used their (obfuscated)
# names, but all personality traits have been made up. I hope they have as much
# fun reading these tests as I had in writing them!

import datetime
import os
import pathlib
import pytest
import time

from .common import TestCommon
from herkules.Herkules import herkules


FIXTURE_DIR = pathlib.Path('tests') / 'beetle'

TEST_FILES = [
    '.hiddendir/.hidden',
    '.hiddendir/.hidden.txt',
    '.hiddendir/multi.dot.longext',
    '.hiddendir/normal.txt',

    '.hiddendir.ext/.hidden',
    '.hiddendir.ext/.hidden.txt',
    '.hiddendir.ext/multi.dot.longext',
    '.hiddendir.ext/normal.txt',

    'dir.ext/.hidden',
    'dir.ext/.hidden.txt',
    'dir.ext/multi.dot.longext',
    'dir.ext/normal.txt',

    'directory/.hidden',
    'directory/.hidden.txt',
    'directory/multi.dot.longext',
    'directory/normal.txt',

    '.hidden',
    '.hidden.txt',
    'multi.dot.longext',
    'normal.txt',
]

TEST_FILES_AND_DIRS = []

for entry in TEST_FILES:
    if entry.endswith('/.hidden'):
        TEST_FILES_AND_DIRS.append(entry.removesuffix('/.hidden'))
    TEST_FILES_AND_DIRS.append(entry)


def set_mtime_to_current_time(dir_path):
    for path_in_directory in herkules(dir_path, include_directories=True):
        os.utime(path_in_directory, times=None)


class TestBeetle(TestCommon):

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_default_options(self, datafiles):
        actual_paths = herkules(
            datafiles)

        expected_files = TEST_FILES
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_directories_in_between(self, datafiles):
        actual_paths = herkules(
            datafiles,
            directories_first=False)

        expected_files = TEST_FILES[-4:]
        expected_files.extend(TEST_FILES[:-4])

        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_directories_included(self, datafiles):
        actual_paths = herkules(
            datafiles,
            include_directories=True,
            directories_first=True)

        expected_files = TEST_FILES_AND_DIRS
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_directories_included_in_between(self, datafiles):
        actual_paths = herkules(
            datafiles,
            include_directories=True,
            directories_first=False)

        expected_files = TEST_FILES_AND_DIRS[-4:]
        expected_files.extend(TEST_FILES_AND_DIRS[:-4])

        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_selector_empty(self, datafiles):
        SELECTOR = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
            ],
            'included_file_names': [
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = TEST_FILES
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_star_1(self, datafiles):
        SELECTOR = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
            ],
            'included_file_names': [
                '*',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = TEST_FILES
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_star_2(self, datafiles):
        SELECTOR = {
            'included_file_names': [
                '*',
                '*.txt',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = TEST_FILES
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_1(self, datafiles):
        SELECTOR = {
            'included_file_names': [
                '*.txt',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = [f for f in TEST_FILES
                          if f.endswith('.txt')]
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_2(self, datafiles):
        SELECTOR = {
            'included_file_names': [
                '*.txt',
                '*.longext',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = [f for f in TEST_FILES
                          if f.endswith('.txt')
                          or f.endswith('.longext')]
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_3(self, datafiles):
        SELECTOR = {
            'included_file_names': [
                '*.txt',
                '*.longext',
                '*.ext',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = [f for f in TEST_FILES
                          if f.endswith('.txt')
                          or f.endswith('.longext')]
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_4(self, datafiles):
        SELECTOR = {
            'included_file_names': [
                '*.ext',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = []
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_included_files_6(self, datafiles):
        SELECTOR = {
            'excluded_directory_names': [
            ],
            'included_file_names': [
                'norm*.*',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = [f for f in TEST_FILES
                          if f.endswith('normal.txt')]
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_1(self, datafiles):
        SELECTOR = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
                'normal.txt',
            ],
            'included_file_names': [
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = [f for f in TEST_FILES
                          if not f.endswith('normal.txt')]
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_2(self, datafiles):
        SELECTOR = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
                '.hidden',
            ],
            'included_file_names': [
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = [f for f in TEST_FILES
                          if not f.endswith('.hidden')]
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_3(self, datafiles):
        SELECTOR = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
                '.hidden.txt',
            ],
            'included_file_names': [
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = [f for f in TEST_FILES
                          if not f.endswith('.hidden.txt')]
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_4(self, datafiles):
        SELECTOR = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
                '.hidden.txt',
            ],
            'included_file_names': [
                '*.txt',
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = [f for f in TEST_FILES
                          if f.endswith('.txt')
                          and not f.endswith('.hidden.txt')]
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_5(self, datafiles):
        SELECTOR = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
                'dir.ext',
            ],
            'included_file_names': [
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = TEST_FILES
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_6(self, datafiles):
        SELECTOR = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
                'norm*.*',
            ],
            'included_file_names': [
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = [f for f in TEST_FILES
                          if not f.endswith('normal.txt')]
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_7(self, datafiles):
        SELECTOR = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
                '.hid*.txt',
            ],
            'included_file_names': [
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = [f for f in TEST_FILES
                          if not f.endswith('.hidden.txt')]
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_8(self, datafiles):
        SELECTOR = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
                '*.ext/.hid*.txt',
            ],
            'included_file_names': [
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = [f for f in TEST_FILES
                          if not f.endswith('dir.ext/.hidden.txt')]
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_excluded_files_9(self, datafiles):
        SELECTOR = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
                'dir.ext',
            ],
            'included_file_names': [
            ],
        }

        actual_paths = herkules(
            datafiles,
            selector=SELECTOR)

        expected_files = TEST_FILES
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_modified_1(self, datafiles):
        modified_since = datetime.datetime.now()
        set_mtime_to_current_time(datafiles)

        actual_paths = herkules(
            datafiles,
            include_directories=True,
            modified_since=modified_since.timestamp())

        expected_files = TEST_FILES_AND_DIRS
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_modified_1_in_between(self, datafiles):
        modified_since = datetime.datetime.now()
        set_mtime_to_current_time(datafiles)

        actual_paths = herkules(
            datafiles,
            directories_first=False,
            include_directories=True,
            modified_since=modified_since)

        expected_files = TEST_FILES_AND_DIRS[-4:]
        expected_files.extend(TEST_FILES_AND_DIRS[:-4])

        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_modified_2(self, datafiles):
        # wait for fixture data to settle down
        modified_since = datetime.datetime.now() + datetime.timedelta(seconds=1)

        actual_paths = herkules(
            datafiles,
            include_directories=True,
            modified_since=modified_since)

        expected_files = []
        self.assert_herkules(datafiles, expected_files, actual_paths)


    @pytest.mark.slow()
    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_modified_3(self, datafiles):
        # wait for fixture data to settle down
        modified_since = datetime.datetime.now() + datetime.timedelta(seconds=1)
        time.sleep(1.0)

        new_dir = datafiles.joinpath('new.dir')
        new_dir.mkdir(parents=True)

        new_file = new_dir.joinpath('new.file.txt')
        new_file.write_text('NEW')

        actual_paths = herkules(
            datafiles,
            include_directories=True,
            modified_since=modified_since)

        expected_files = [
            'new.dir',
            'new.dir/new.file.txt',
        ]
        self.assert_herkules(datafiles, expected_files, actual_paths)
