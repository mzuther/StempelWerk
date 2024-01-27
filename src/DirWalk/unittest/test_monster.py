# The story, all names, characters, and incidents portrayed in this test are
# fictitious. No identification with actual persons (living or deceased),
# places, buildings, and products is intended or should be inferred.
#
# In other words: I have great and helpful colleagues with a lot of humour. In
# order to make writing these tests more fun, I have used their (obfuscated)
# names, but all personality traits have been made up. I hope they have as much
# fun reading these tests as I had in writing them!

import pathlib
import pytest

from src.DirWalk.unittest.common import TestCommon
from src.DirWalk.DirWalk import dirwalk


FIXTURE_DIR = pathlib.Path('src/DirWalk/unittest/') / 'monster'

TEST_FILES = [
    '.hidden',
    '.hidden.txt',
    'normal.txt',
    'multi.dot.longext',

    'directory/.hidden',
    'directory/.hidden.txt',
    'directory/normal.txt',
    'directory/multi.dot.longext',

    'dir.ext/.hidden',
    'dir.ext/.hidden.txt',
    'dir.ext/normal.txt',
    'dir.ext/multi.dot.longext',

    '.hiddendir/.hidden',
    '.hiddendir/.hidden.txt',
    '.hiddendir/normal.txt',
    '.hiddendir/multi.dot.longext',

    '.hiddendir.ext/.hidden',
    '.hiddendir.ext/.hidden.txt',
    '.hiddendir.ext/normal.txt',
    '.hiddendir.ext/multi.dot.longext',
]


class TestMonster(TestCommon):

    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_no_options(self, datafiles):
        found_paths = dirwalk(datafiles)

        self.assert_dirwalk(datafiles, found_paths, TEST_FILES,
                            ignore_order=True)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_inclusions_empty(self, datafiles):
        INCLUSIONS = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
            ],
            'included_suffixes': [
            ],
        }

        found_paths = dirwalk(datafiles,
                              included=INCLUSIONS)

        self.assert_dirwalk(datafiles, found_paths, TEST_FILES,
                            ignore_order=True)


    @pytest.mark.datafiles(FIXTURE_DIR)
    def test_inclusions_star(self, datafiles):
        INCLUSIONS = {
            'excluded_directory_names': [
            ],
            'excluded_file_names': [
            ],
            'included_suffixes': [
                '*',
            ],
        }

        found_paths = dirwalk(datafiles,
                              included=INCLUSIONS)

        self.assert_dirwalk(datafiles, found_paths, TEST_FILES,
                            ignore_order=True)
