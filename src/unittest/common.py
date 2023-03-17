import contextlib
import difflib
import filecmp
import json
import pathlib
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
        root_dir = pathlib.Path(config['root_dir'])
        autocreated_paths = ['template_dir', 'output_dir']

        for dir_key in autocreated_paths:
            dir_path = root_dir / config[dir_key]
            # directories that should be autocreated do not exist yet
            if pre_check:
                assert not dir_path.is_dir(), \
                    f'directory "{dir_path}" already exists'
            # directories were autocreated
            else:
                assert dir_path.is_dir(), \
                    f'directory "{dir_path}" was not created'

    # ------------------------------------------------------------------------

    def create_config(self, custom_config, output_path, filename):
        output_path = pathlib.Path(output_path)
        config_path = output_path / filename

        config = {
            'root_dir': str(output_path),
            'template_dir': '10-templates',
            'output_dir': '20-output',
            # ----------------------------------------
            'included_suffixes': [
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
            'marker_content': '### Content:',
            'newline': '\n'
        }

        # update config with custom settings
        config.update(custom_config)

        contents = json.dumps(config, ensure_ascii=False, indent=2)
        config_path.write_text(contents)

        return config_path


    def compare_directories(self, config):
        root_dir = pathlib.Path(config['root_dir'])
        output_path = root_dir / config['output_dir']
        expected_base = root_dir / '30-expected'

        comparator = filecmp.dircmp(expected_base, output_path)

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

            path_expected = expected_base / differing_file_path
            with path_expected.open() as f:
                expected_contents = f.readlines()

            path_real = output_path / differing_file_path
            with path_real.open() as f:
                real_contents = f.readlines()

            result = difflib.unified_diff(
                expected_contents,
                real_contents,
                fromfile=str(path_expected),
                tofile=str(path_real))

            print('------------------------------------------------------')
            print()
            print('Difference between expected output and result:')
            print()
            sys.stdout.writelines(result)
            print()

            assert False, 'Found differing files.'

    # ------------------------------------------------------------------------

    def init_stempelwerk(self, config_path=None, global_namespace=None,
                         process_only_modified=False):
        script_path = sys.argv[0]
        command_line_arguments = [script_path]

        if global_namespace:
            command_line_arguments.append('--globals')
            command_line_arguments.append(global_namespace)

        if process_only_modified:
            command_line_arguments.append('--only-modified')

        # allow testing for missing configuration on command line
        if config_path:
            command_line_arguments.append(str(config_path))

        parsed_args = StempelWerk.CommandLineParser(command_line_arguments)
        instance = StempelWerk(parsed_args.settings, parsed_args.verbosity)

        return instance, parsed_args


    def run(self, config_path=None, global_namespace=None,
            process_only_modified=False):
        instance, parsed_args = self.init_stempelwerk(
            config_path, global_namespace, process_only_modified)

        assert parsed_args.process_only_modified == \
            process_only_modified

        results = instance.process_templates(process_only_modified)
        results['instance'] = instance

        return results


    def run_with_config_file(self, config_path, resource_directory,
                             global_namespace=None):
        contents = config_path.read_text()
        config = json.loads(contents)

        print('Configuration:')
        print(json.dumps(config, ensure_ascii=False, indent=2))

        results = self.run(config_path, global_namespace)
        results['configuration'] = config

        return results


    def run_and_compare(self, config_path, resource_path,
                        global_namespace=None):
        results = self.run_with_config_file(
            config_path, resource_path, global_namespace)

        self.compare_directories(
            results['configuration'])

        return results
