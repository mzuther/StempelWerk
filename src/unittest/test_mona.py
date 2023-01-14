# The story, all names, characters, and incidents portrayed in this
# test are fictitious.  No identification with actual persons (living
# or deceased), places, buildings, and products is intended or should
# be inferred.
#
# In other words: I have great and helpful colleagues with a lot of
# humour.  In order to make writing these tests more fun, I have used
# their names, but all personality traits have been made up.  I hope
# they have as much fun reading these tests as I had in writing them!

import sys

import pytest
from src.StempelWerk import StempelWerk


class TestMona:
    # Mona is an inquisitive developer and loves to try new things.
    # She found StempelWerk on GitHub, cloned it and wants to get her
    # hands dirty.
    #
    # Reading manuals is for beginners, so Mona starts StempelWerk.
    # It immediately fails because she did not provide a configuration
    # file.  But she gets a nice error message to that regard.
    def test_error_missing_config(self, capsys):
        with pytest.raises(SystemExit):
            argv = [sys.argv[0]]
            StempelWerk(argv)

        error_message = 'the following arguments are required: CONFIG_FILE'
        captured = capsys.readouterr()
        assert error_message in captured.err


    # Mona adds a config path to the command line, but forgets to
    # create the file.  Thankfully, she gets another error message.
    def test_error_missing_config_2(self, capsys):
        with pytest.raises(SystemExit):
            argv = [sys.argv[0], './settings.json']
            StempelWerk(argv)

        captured = capsys.readouterr()
        assert 'not found' in captured.out
