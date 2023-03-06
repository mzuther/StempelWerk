# The story, all names, characters, and incidents portrayed in this test are
# fictitious. No identification with actual persons (living or deceased),
# places, buildings, and products is intended or should be inferred.
#
# In other words: I have great and helpful colleagues with a lot of humour. In
# order to make writing these tests more fun, I have used their names, but all
# personality traits have been made up. I hope they have as much fun reading
# these tests as I had in writing them!

import json
import os

import pytest
from src.unittest.common import TestCommon


class TestNitram(TestCommon):
    def run_and_compare(self, config_path, unit_test_directory):
        unit_test_path = os.path.join(
            './src/unittest/nitram/',
            unit_test_directory)

        return super().run_and_compare(
            config_path,
            unit_test_path)


    def test_process_only_modified_1(self, tmp_path):

        def convenience_run(partial_run, matching):
            self.run(
                config_path,
                process_only_modified=partial_run)

            if matching:
                self.compare_directories(config)
            else:
                with pytest.raises(AssertionError):
                    self.compare_directories(config)


        def remove_file(partial_file_path):
            output_path = os.path.join(tmp_path, partial_file_path)
            os.remove(output_path)

            # assert deletion
            with pytest.raises(AssertionError):
                self.compare_directories(config)


        def modify_file(partial_file_path):
            output_path = os.path.join(tmp_path, partial_file_path)

            with open(output_path, 'r') as f:
                contents = f.readlines()

            # delete first line
            contents = contents[1:]

            with open(output_path, 'w') as f:
                f.writelines(contents)

            # assert modification
            with pytest.raises(AssertionError):
                self.compare_directories(config)

        # ---------------------------------------------------------------------

        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_directory = '1_process_only_modified_1'

        with open(config_path, mode='r') as f:
            config = json.load(f)

        # set up StempelWerk and execute full run
        self.run_and_compare(config_path, unit_test_directory)

        # full run renders all files unconditonally
        remove_file('20-output/ab.txt')
        modify_file('20-output/cd.txt')
        convenience_run(partial_run=False, matching=True)

        # partial run leaves deleted output file alone
        remove_file('20-output/cd.txt')
        convenience_run(partial_run=True, matching=False)

        # full run re-creates all output files
        convenience_run(partial_run=False, matching=True)

        # partial run does not render externally modified output file
        modify_file('20-output/ab.txt')
        convenience_run(partial_run=True, matching=False)

        # full run also renders externally modified output files
        convenience_run(partial_run=False, matching=True)



    def test_lean_template_removal(self, tmp_path):

        def convenience_run(partial_run, matching):
            self.run(
                config_path,
                process_only_modified=partial_run)

            if matching:
                self.compare_directories(config)
            else:
                with pytest.raises(AssertionError):
                    self.compare_directories(config)


        def remove_file(partial_file_path):
            output_path = os.path.join(tmp_path, partial_file_path)
            os.remove(output_path)

        # ---------------------------------------------------------------------

        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        unit_test_directory = '1_process_only_modified_1'

        with open(config_path, mode='r') as f:
            config = json.load(f)

        # set up StempelWerk and execute full run
        self.run_and_compare(config_path, unit_test_directory)

        # deleting a template leaves the output file alone
        remove_file('10-templates/ab.jinja')
        convenience_run(partial_run=False, matching=True)
