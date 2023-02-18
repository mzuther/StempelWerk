# The story, all names, characters, and incidents portrayed in this test are
# fictitious. No identification with actual persons (living or deceased),
# places, buildings, and products is intended or should be inferred.
#
# In other words: I have great and helpful colleagues with a lot of humour. In
# order to make writing these tests more fun, I have used their names, but all
# personality traits have been made up. I hope they have as much fun reading
# these tests as I had in writing them!

import contextlib
import difflib
import filecmp
import json
import os
import shutil
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
            'template_dir': '10-templates/',
            'output_dir': '20-output/',
            # ----------------------------------------
            'included_file_extensions': [
                '*.jinja'
            ],
            'stencil_dir_name': '',
            'create_directories': False,
            # ----------------------------------------
            'jinja_options': {
                'trim_blocks': True,
            },
            'jinja_extensions': [],
            'custom_modules': [],
            # ----------------------------------------
            'last_run_file': '.last_run',
            'marker_new_file': '### New file:',
            'marker_content': '### Content:'
        }

        # update config with custom settings
        config.update(custom_config)

        with open(config_path, mode='w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return config_path


    def copy_directory_tree(self, config, source_path):
        destination_path = config['root_dir']
        shutil.copytree(source_path, destination_path,
                        dirs_exist_ok=True)


    def compare_directories(self, config):
        root_dir = config['root_dir']
        output_path = os.path.join(root_dir, config['output_dir'])
        expected_path = os.path.join(root_dir, '30-expected')

        comparator = filecmp.dircmp(expected_path, output_path)

        assert not comparator.left_only, \
            f'these files were not generated: { comparator.left_only }'
        assert not comparator.right_only, \
            f'unexpected files were generated: { comparator.right_only }'

        assert not comparator.common_funny, \
            f'could not process these files: { comparator.common_funny }'
        assert not comparator.funny_files, \
            f'could not compare these files: { comparator.funny_files }'

        if comparator.diff_files:
            # only print first differing file
            differing_file_path = comparator.diff_files[0]

            path_expected = os.path.join(expected_path, differing_file_path)
            with open(path_expected, mode='r') as f:
                expected_contents = f.readlines()

            path_real = os.path.join(output_path, differing_file_path)
            with open(path_real, mode='r') as f:
                real_contents = f.readlines()

            result = difflib.unified_diff(
                expected_contents,
                real_contents,
                fromfile=path_expected,
                tofile=path_real)

            print('------------------------------------------------------')
            print()
            print('Difference between expected output and result:')
            print()
            sys.stdout.writelines(result)
            print()

            assert False, 'Found differing files.'

    # ------------------------------------------------------------------------

    def run(self, config_path):
        argv = [sys.argv[0], config_path]
        sw = StempelWerk(argv)
        sw.process_templates()


    def run_with_config(self, config, output_path, filename='settings.json'):
        config_path = self.create_config(config, output_path, filename)
        self.run(config_path)


    def run_and_compare(self, config_path, unit_test_path):
        unit_test_path = os.path.join('./src/unittest/mona/', unit_test_path)

        with open(config_path, mode='r') as f:
            config = json.load(f)

            print('Configuration:')
            print(json.dumps(config, ensure_ascii=False, indent=2))

        self.copy_directory_tree(config, unit_test_path)
        self.run(config_path)
        self.compare_directories(config)

    # ------------------------------------------------------------------------

    # Mona is an inquisitive developer and loves to try new things. She found
    # StempelWerk on GitHub, cloned it and wants to get her hands dirty.
    #
    # Reading manuals is for beginners, so Mona starts StempelWerk. It
    # immediately fails because she did not provide a configuration file. But
    # she gets a nice error message to that regard.
    def test_error_on_missing_config(self, capsys):
        with pytest.raises(SystemExit):
            argv = [sys.argv[0]]
            StempelWerk(argv)

        error_message = 'the following arguments are required: CONFIG_FILE'
        captured = capsys.readouterr()
        assert error_message in captured.err


    # Mona adds a config path to the command line, but forgets to create the
    # file. Thankfully, she gets another error message.
    def test_error_on_missing_config_2(self, capsys):
        with pytest.raises(SystemExit):
            self.run('./settings.json')

        captured = capsys.readouterr()
        assert 'not found' in captured.out


    # After creating a config file, Mona is impressed that StempelWerk saves her
    # some work by automatically creating the template and output directories.
    # She is also pleased that she is able to concentrate on the task and does
    # not have to provide any templates.
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


    # Mona finally reads (a small part of) the documentation. She dreams of
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

        with open(config_path, mode='r') as f:
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

        with open(config_path, mode='r') as f:
            config = json.load(f)

        # implicitly check that StempelWerk runs without any templates
        with self.does_not_raise(SystemExit):
            self.assert_autocreated_paths(config, pre_check=True)
            self.run(config_path)
            self.assert_autocreated_paths(config, pre_check=False)

    # ------------------------------------------------------------------------

    # Mona decides to finally write a template. She rather likes the alphabet
    # and comes up with a brainy scheme of printing multiples of her favorite
    # characters without touching the keyboard. It works!
    def test_render_notrim(self, tmp_path):
        # assert that StempelWerk can change Jinja options
        config = {
            'jinja_options': {
                'trim_blocks': False,
            },
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_path = '1_template_1_notrim'
        self.run_and_compare(config_path, unit_test_path)


    # Mona decides that she will try enabling "trim_blocks". After seeing the
    # results, she concurs with the author of StempelWerk that this option
    # should always be enabled.
    def test_render_trim(self, tmp_path):
        # "trim_blocks" is set to "True" by default in "create_config"
        config = {}

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_path = '1_template_2_trim'
        self.run_and_compare(config_path, unit_test_path)


    # The real power of templates lies in preventing DRY ("do not repeat
    # yourself"). Accordingly, Mona writes a template that creates two files,
    # but shares their settings and macros.
    def test_render_splitfile(self, tmp_path):
        # assert that a subdirectory under "tmp_path" also works
        root_dir = os.path.join(str(tmp_path), 'DRY')

        config = {
            'root_dir': root_dir,
            'included_file_extensions': [
                '*.txt.jinja',
            ],
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_path = '1_template_3_splitfile'

        # assert indirectly that the template file "ignored.jinja" is
        # ignored and not processed
        self.run_and_compare(config_path, unit_test_path)

        assert os.path.isfile(
            os.path.join(root_dir, '30-expected/ab.txt')
        )


    # Mona loves Wikipedia and articles on programming languages
    # (https://en.wikipedia.org/wiki/Esoteric_programming_language). She wants
    # to have her very own article and creates "MonaTalk". Variables are
    # declared by prepending "###", so she is happy that StempelWerk allows her
    # to redefine file separators.
    #
    # ### Hello: world
    #
    # However, Mona forgot that file separators need to be changed in the
    # configuration. So she is greeted by a nice error message.
    def test_render_file_separator_code_only(self, tmp_path):
        config = {}

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_path = '1_template_4_file_separator'
        with pytest.raises(SystemExit):
            self.run_and_compare(config_path, unit_test_path)


    # After updating the configuration, Mona gets the output she is looking for.
    #
    # Meanwhile, Mona's article on Wikipedia was deleted based on the
    # far-fetched argument that MonaTalk is only Turing-complete on Fridays.
    # Mona is now looking for a good lawyer to get the article back. Good luck
    # with that!
    def test_render_file_separator(self, tmp_path):
        config = {
            'marker_new_file': 'START_FILE',
            'marker_content': 'START_CONTENT'
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_path = '1_template_4_file_separator'
        self.run_and_compare(config_path, unit_test_path)


    # Mona changes the default name of the stencil directory, but forgets to
    # update the settings file. StempelWerk fails, but displays a helpful error
    # message.
    def test_render_missing_stencil(self, tmp_path):
        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_path = '1_template_5_with_stencil'
        with pytest.raises(SystemExit):
            self.run_and_compare(config_path, unit_test_path)


    # After updating the settings file, StempelWerk runs just fine.
    def test_render_with_stencil(self, tmp_path):
        config = {
            'stencil_dir_name': '00-stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_path = '1_template_5_with_stencil'
        self.run_and_compare(config_path, unit_test_path)


    # Mona wants to create different files using different stencils. StempelWerk
    # just yawns and goes back to sleep.
    def test_render_multiple_stencils(self, tmp_path):
        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_path = '1_template_6_multiple_stencils'
        self.run_and_compare(config_path, unit_test_path)


    # Mona tries to render a file into a subdirectory of the output directory.
    # StempelWerk expects subdirectories to already exist and thus exits with an
    # error message.
    def test_render_create_subdirectories_1(self, tmp_path):
        config = {}

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_path = '1_template_7_create_subdirs'
        with pytest.raises(SystemExit):
            self.run_and_compare(config_path, unit_test_path)


    # When Mona creates the subdirectory before running StempelWerk, everything
    # works as expected.
    def test_render_create_subdirectories_2(self, tmp_path):
        config = {}

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        # create output subdirectory by hand
        os.makedirs(os.path.join(tmp_path, '20-output/other_name'))

        unit_test_path = '1_template_7_create_subdirs'
        self.run_and_compare(config_path, unit_test_path)


    # Enabling the automatic creation of missing directories works just as well,
    # at the price of incuding a security risk.
    def test_render_create_subdirectories_3(self, tmp_path):
        config = {
            'create_directories': True
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_path = '1_template_7_create_subdirs'
        self.run_and_compare(config_path, unit_test_path)


    # After playing around with a single template, Mona is excited that
    # StempelWerk can process multiple templates. In a single run!!!
    def test_render_multi_no_stencil(self, tmp_path):
        config = {}

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_path = '2_templates_1_no_stencil'
        self.run_and_compare(config_path, unit_test_path)


    # When the excitement has worn off, she verifies that common template code
    # can be reused by moving it into a stencil.
    def test_render_multi_with_stencil(self, tmp_path):
        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_path = '2_templates_2_with_stencil'
        self.run_and_compare(config_path, unit_test_path)
