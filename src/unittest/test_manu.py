# The story, all names, characters, and incidents portrayed in this test are
# fictitious. No identification with actual persons (living or deceased),
# places, buildings, and products is intended or should be inferred.
#
# In other words: I have great and helpful colleagues with a lot of humour. In
# order to make writing these tests more fun, I have used their (obfuscated)
# names, but all personality traits have been made up. I hope they have as much
# fun reading these tests as I had in writing them!

import json
import pathlib
import os

import pytest
from src.unittest.common import TestCommon


class TestManu(TestCommon):
    @property
    def resource_base_path(self):
        return pathlib.Path('src/unittest/') / 'manu'


    # Manu is an inquisitive developer and loves to try new things. She found
    # StempelWerk on GitHub, cloned it and wants to get her hands dirty.
    #
    # Reading manuals is for beginners, so Manu starts StempelWerk. It
    # immediately fails because she did not provide a configuration file. But
    # she gets a nice error message to that regard.
    def test_error_on_missing_config(self, capsys):
        with pytest.raises(SystemExit):
            self.run(None)

        error_message = 'the following arguments are required: CONFIG_FILE'
        captured = capsys.readouterr()
        assert error_message in captured.err


    # Manu adds a config path to the command line, but forgets to create the
    # file. Thankfully, she gets another error message.
    def test_error_on_missing_config_2(self, capsys):
        with pytest.raises(SystemExit):
            self.run('./settings.json')

        captured = capsys.readouterr()
        assert 'not found' in captured.out


    # After creating a config file, Manu is impressed that StempelWerk saves her
    # some work by automatically creating the template and output directories.
    # She is also pleased that she is able to concentrate on the task and does
    # not have to provide any templates.
    def test_autocreation_of_directories(self, tmp_path):
        config = {}

        config_path = self.create_config(
            config, tmp_path, 'settings_unique.json')

        with config_path.open() as f:
            config = json.load(f)

        # implicitly check that StempelWerk runs without any templates
        with self.does_not_raise(SystemExit):
            self.assert_autocreated_paths(config, pre_check=True)
            self.run(config_path)
            self.assert_autocreated_paths(config, pre_check=False)


    # Manu finally reads (a small part of) the documentation. She dreams of
    # leaving the DOS ecosystem behind, so she verfifies that paths can really
    # be specified in a cross-platform way.
    def test_path_separators(self, tmp_path):
        # common path separator can be used (cross-platform support)
        tmp_path = str(tmp_path).replace(os.sep, '/')

        # paths without trailing path separator are functional
        config = {
            'template_dir': 'templates/',
            'output_dir': 'output/'
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        with config_path.open() as f:
            config = json.load(f)

        # implicitly check that StempelWerk runs without any templates
        with self.does_not_raise(SystemExit):
            self.assert_autocreated_paths(config, pre_check=True)
            self.run(config_path)
            self.assert_autocreated_paths(config, pre_check=False)


    # She also dislikes trailing path separators (if DOS does not need them, why
    # should any other OS?) and stubbornly removes them. StempelWerk just smiles
    # and keeps on working as before.
    def test_path_separators_trailing(self, tmp_path):
        # common path separator can be used (cross-platform support)
        tmp_path = str(tmp_path).replace(os.sep, '/')

        # paths without trailing path separator are functional
        config = {
            'template_dir': 'templates',
            'output_dir': 'output'
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        with config_path.open() as f:
            config = json.load(f)

        # implicitly check that StempelWerk runs without any templates
        with self.does_not_raise(SystemExit):
            self.assert_autocreated_paths(config, pre_check=True)
            self.run(config_path)
            self.assert_autocreated_paths(config, pre_check=False)

    # ------------------------------------------------------------------------

    # Manu decides to finally write a template. She rather likes the alphabet
    # and comes up with a brainy scheme of printing multiples of her favorite
    # characters without touching the keyboard. It works!
    def test_render_notrim(self, tmp_path):
        resource_directory = '1_template_1_notrim'

        # assert that StempelWerk can change Jinja options
        config = {
            'jinja_options': {
                'trim_blocks': False,
            },
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        self.run_and_compare(config_path, resource_directory)


    # Manu decides that she will try enabling "trim_blocks". After seeing the
    # results, she concurs with the author of StempelWerk that this option
    # should always be enabled.
    def test_render_trim(self, tmp_path):
        resource_directory = '1_template_2_trim'

        # "trim_blocks" is set to "True" by default in "create_config"
        config = {}

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        self.run_and_compare(config_path, resource_directory)


    # The real power of templates lies in preventing DRY ("do not repeat
    # yourself"). Accordingly, Manu writes a template that creates two files,
    # but shares their settings and macros.
    def test_render_splitfile(self, tmp_path):
        resource_directory = '1_template_3_splitfile'

        # assert that a subdirectory under "tmp_path" also works
        root_dir = tmp_path / 'DRY/nested'

        config = {
            'root_dir': str(root_dir),
            'included_suffixes': [
                '*.included.jinja',
            ],
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        # assert indirectly that the template file "ignored.jinja" is
        # ignored and not processed
        self.run_and_compare(config_path, resource_directory)


    # Manu loves Wikipedia and articles on programming languages
    # (https://en.wikipedia.org/wiki/Esoteric_programming_language). She wants
    # to have her very own article and creates "ManuTalk". Variables are
    # declared by prepending "###", so she is happy that StempelWerk allows her
    # to redefine file separators.
    #
    # ### Hello: world
    #
    # However, Manu forgot that file separators need to be changed in the
    # configuration. So she is greeted by a nice error message.
    def test_render_file_separator_code_only(self, tmp_path):
        resource_directory = '1_template_4_file_separator'

        config = {}

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        with pytest.raises(SystemExit):
            self.run_and_compare(config_path, resource_directory)


    # After updating the configuration, Manu gets the output she is looking for.
    #
    # Meanwhile, Manu's article on Wikipedia was deleted based on the
    # far-fetched argument that ManuTalk is only Turing-complete on Fridays.
    # Manu is now looking for a good lawyer to get the article back. Good luck
    # with that!
    def test_render_file_separator(self, tmp_path):
        resource_directory = '1_template_4_file_separator'

        config = {
            'marker_new_file': 'START_FILE',
            'marker_content': 'START_CONTENT'
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        self.run_and_compare(config_path, resource_directory)


    # Manu changes the default name of the stencil directory, but forgets to
    # update the settings file. StempelWerk fails, but displays a helpful error
    # message.
    def test_render_missing_stencil(self, tmp_path):
        resource_directory = '1_template_5_with_stencil'

        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        with pytest.raises(SystemExit):
            self.run_and_compare(config_path, resource_directory)


    # After updating the settings file, StempelWerk runs just fine.
    def test_render_with_stencil(self, tmp_path):
        resource_directory = '1_template_5_with_stencil'

        config = {
            'stencil_dir_name': '00-stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        self.run_and_compare(config_path, resource_directory)


    # Manu wants to create different files using different stencils. StempelWerk
    # just yawns and goes back to sleep.
    def test_render_multiple_stencils(self, tmp_path):
        resource_directory = '1_template_6_multiple_stencils'

        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        self.run_and_compare(config_path, resource_directory)


    # Manu tries to render a file into a subdirectory of the output directory.
    # StempelWerk expects subdirectories to already exist and thus exits with an
    # error message.
    def test_render_create_subdirectories_1(self, tmp_path):
        resource_directory = '1_template_7_create_subdirs'

        config = {}

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        with pytest.raises(SystemExit):
            self.run_and_compare(config_path, resource_directory)


    # When Manu creates the subdirectory before running StempelWerk, everything
    # works as expected.
    def test_render_create_subdirectories_2(self, tmp_path):
        resource_directory = '1_template_7_create_subdirs'

        config = {}

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        # create nested output subdirectory by hand
        output_subpath = tmp_path / '20-output/other/name'
        output_subpath.mkdir(parents=True)

        self.run_and_compare(config_path, resource_directory)


    # Enabling the automatic creation of missing directories works just as well,
    # at the price of incuding a security risk.
    def test_render_create_subdirectories_3(self, tmp_path):
        resource_directory = '1_template_7_create_subdirs'

        config = {
            'create_directories': True
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        self.run_and_compare(config_path, resource_directory)


    # Manu is intrigued: different operating systems store text files with
    # different newline characters. Time to have some fun!
    def test_render_file_endings_1(self, tmp_path):
        resource_directory = '1_template_8_file_endings'

        config = {
            'create_directories': True,
            'newline': '\n'
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        self.run_and_compare(config_path, resource_directory)


    # Can StempelWerk's newline logic be turned on its head? Yes, ma'am!
    def test_render_file_endings_2(self, tmp_path):
        resource_directory = '1_template_8_file_endings'

        config = {
            'create_directories': True,
            # invert logic, part 1
            'newline': '\r\n'
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        results = self.run_with_config_file(config_path, resource_directory)
        instance = results['instance']

        instance.newline_exceptions = {
            # invert logic, part 2
            '.txt': '\n',
        }

        instance.process_templates()
        self.compare_directories(
            results['configuration'])


    # After playing around with a single template, Manu is excited that
    # StempelWerk can process multiple templates. In a single run!!!
    def test_render_multi_no_stencil(self, tmp_path):
        resource_directory = '2_templates_1_no_stencil'

        config = {}

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        self.run_and_compare(config_path, resource_directory)


    # When the excitement has worn off, she verifies that common template code
    # can be reused by moving it into a stencil.
    def test_render_multi_with_stencil(self, tmp_path):
        resource_directory = '2_templates_2_with_stencil'

        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        self.run_and_compare(config_path, resource_directory)
