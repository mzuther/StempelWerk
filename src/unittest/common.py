import contextlib
import difflib
import filecmp
import json
import os
import shutil
import sys

import pytest
from src.StempelWerk import StempelWerk


class TestCommon:
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

    def run(self, config_path=None, only_updated=False):
        script_path = sys.argv[0]
        command_line_arguments = [script_path]

        # allow testing for missing configuration on command line
        if config_path:
            command_line_arguments.append(config_path)

        if only_updated:
            command_line_arguments.append('--only-modified')

        args = StempelWerk.parse_command_line(command_line_arguments)
        sw = StempelWerk(args)

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
