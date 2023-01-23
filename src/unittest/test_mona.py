# The story, all names, characters, and incidents portrayed in this
# test are fictitious.  No identification with actual persons (living
# or deceased), places, buildings, and products is intended or should
# be inferred.
#
# In other words: I have great and helpful colleagues with a lot of
# humour.  In order to make writing these tests more fun, I have used
# their names, but all personality traits have been made up.  I hope
# they have as much fun reading these tests as I had in writing them!

import contextlib
import json
import os
import sys

import pytest
from src.StempelWerk import StempelWerk


class TestMona:
    # adapted from https://stackoverflow.com/a/42327075
    @contextlib.contextmanager
    def does_not_raise(self, exception):
        try:
            yield
        except exception:
            raise pytest.fail(f'raised unwanted exception {exception}')


    def assert_autocreated_paths(self, config, pre_check):
        root_dir = config['root_dir']
        autocreated_paths = ['template_dir', 'output_dir']

        for dir_key in autocreated_paths:
            dir_path = os.path.join(root_dir, config[dir_key])
            # directories that should be autocreated do not exist yet
            if pre_check:
                assert not os.path.isdir(dir_path), \
                    f'directory "{dir_path}" already exists'
            # directories were autocreated
            else:
                assert os.path.isdir(dir_path), \
                    f'directory "{dir_path}" was not created'

    # ------------------------------------------------------------------------

    def create_config(self, custom_config, output_path, filename):
        config_path = os.path.join(output_path, filename)
        config = {
            'root_dir': str(output_path),
            'template_dir': 'templates/',
            'output_dir': 'output/',
            'stencil_dir_name': 'stencils',
            'included_file_extensions': [
                '*.jinja'
            ],
        }

        # update config with custom settings
        config.update(custom_config)

        with open(config_path, mode='w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return config_path

    # ------------------------------------------------------------------------

    def run(self, config_path):
        argv = [sys.argv[0], config_path]
        sw = StempelWerk(argv)
        sw.process_templates()


    def run_with_config(self, config, output_path, filename='settings.json'):
        config_path = self.create_config(config, output_path, filename)
        self.run(config_path)

    # ------------------------------------------------------------------------

    # Mona is an inquisitive developer and loves to try new things.
    # She found StempelWerk on GitHub, cloned it and wants to get her
    # hands dirty.
    #
    # Reading manuals is for beginners, so Mona starts StempelWerk.
    # It immediately fails because she did not provide a configuration
    # file.  But she gets a nice error message to that regard.
    def test_error_on_missing_config(self, capsys):
        with pytest.raises(SystemExit):
            argv = [sys.argv[0]]
            StempelWerk(argv)

        error_message = 'the following arguments are required: CONFIG_FILE'
        captured = capsys.readouterr()
        assert error_message in captured.err


    # Mona adds a config path to the command line, but forgets to
    # create the file.  Thankfully, she gets another error message.
    def test_error_on_missing_config_2(self, capsys):
        with pytest.raises(SystemExit):
            self.run('./settings.json')

        captured = capsys.readouterr()
        assert 'not found' in captured.out


    # After creating a config file, Mona is impressed that StempelWerk
    # saves her some work by automatically creating the template and
    # output directories.  She is also pleased that she is able to
    # concentrate on the task and does not have to provide any
    # templates.
    def test_autocreation_of_directories(self, tmp_path):
        config = {}

        config_path = self.create_config(
            config, tmp_path, 'settings_unique.json')

        with open(config_path, mode='r') as f:
            config = json.load(f)

        # implicitly check that StempelWerk runs without any templates
        with self.does_not_raise(SystemExit):
            self.assert_autocreated_paths(config, pre_check=True)
            self.run(config_path)
            self.assert_autocreated_paths(config, pre_check=False)


    # Mona finally reads (a small part of) the documentation.  She
    # dreams of leaving the DOS ecosystem behind, so she verfifies
    # that paths can really be specified in a cross-platform way.  She
    # also dislikes trailing path separators (if DOS does not need
    # them, why should any other OS?) and stubbornly removes them.
    # StempelWerk just smiles and keeps on working as before.
    def test_path_separators(self, tmp_path):
        # common path separator can be used (cross-platform support)
        tmp_path = str(tmp_path).replace(os.sep, '/')

        # paths without trailing path separator are functional
        config = {
            'template_dir': 'templates',
            'output_dir': 'output'
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        with open(config_path, mode='r') as f:
            config = json.load(f)

        # implicitly check that StempelWerk runs without any templates
        with self.does_not_raise(SystemExit):
            self.assert_autocreated_paths(config, pre_check=True)
            self.run(config_path)
            self.assert_autocreated_paths(config, pre_check=False)
