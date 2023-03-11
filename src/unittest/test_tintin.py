# The story, all names, characters, and incidents portrayed in this test are
# fictitious. No identification with actual persons (living or deceased),
# places, buildings, and products is intended or should be inferred.
#
# In other words: I have great and helpful colleagues with a lot of humour. In
# order to make writing these tests more fun, I have used their (obfuscated)
# names, but all personality traits have been made up. I hope they have as much
# fun reading these tests as I had in writing them!

import os

import pytest
from src.unittest.common import TestCommon


class TestTinTin(TestCommon):
    def run_with_config_file(self, config_path, unit_test_directory,
                             global_namespace=None):
        unit_test_path = os.path.join(
            './src/unittest/tintin/',
            unit_test_directory)

        return super().run_with_config_file(
            config_path,
            unit_test_path,
            global_namespace=global_namespace)

    # ---------------------------------------------------------------------

    # Tin Tin lead a double life: he was both developer and a chairman of the
    # UTP (Union of Technology Purloiners). After "obtaining" StempelWerk from a
    # project, he noticed with horror that he had stolen free software - a faux
    # pas of the highest degree.
    #
    # Not much has changed - Tin Tin still leads a double life. He is now both
    # prison inmate and UTP outcast. To reduce his sentence (150 years) by a few
    # days, he agreed to test the more intricate parts of StempelWerk.
    #
    # As a thief who made the global news, he obviously starts by testing global
    # variables.
    def test_global_variables(self, tmp_path):
        unit_test_directory = '1_global_variables'
        global_namespace = '{"NO_cast": true}'

        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        # set up StempelWerk and execute full run
        self.run_and_compare(
            config_path, unit_test_directory,
            global_namespace=global_namespace)


    # After a year of intense testing, Tin Tin moved on to custom modules. He
    # wanted to call them "prison_cell" and "inmate_canteen", but the author of
    # StempelWerk put his foot down.
    def test_custom_module(self, tmp_path):
        unit_test_directory = '2_custom_module'

        config = {
            'stencil_dir_name': 'stencils',
            'custom_modules': [
                'src.custom.add_filters',
                'src.custom.add_tests',
            ],
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        # set up StempelWerk and execute full run
        self.run_and_compare(config_path, unit_test_directory)


    # Only 148 years to go! At Tin Tin's current pace, he will run out of work
    # by the end of the century ...
    #
    # Anyway, he recently started testing Jinja extensions. We will keep you
    # posted on his progress. Don't expect news anytime soon, though.
    def test_jinja_extension(self, tmp_path):

        def file_exists(partial_file_path):
            file_path = os.path.join(tmp_path, partial_file_path)
            if not os.path.isfile(file_path):
                raise FileNotFoundError(file_path)


        def remove_file(partial_file_path):
            output_path = os.path.join(tmp_path, partial_file_path)
            os.remove(output_path)

        # ---------------------------------------------------------------------

        unit_test_directory = '3_jinja_extension'
        debug_file = '20-output/Debug.txt'

        config = {
            'stencil_dir_name': 'stencils',
            'jinja_extensions': [
                'jinja2.ext.debug',
            ],
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        with pytest.raises(FileNotFoundError):
            file_exists(debug_file)

        # set up StempelWerk and execute full run
        results = self.run_with_config_file(
            config_path, unit_test_directory)

        file_exists(debug_file)

        with open(os.path.join(tmp_path, debug_file)) as f:
            debug_output = f.read()
            print(debug_output)

            stencils = [
                'stencils/00-common_settings.sql.jinja',
                'stencils/10-sql_create_table.sql.jinja',
                'stencils/20-sql_create_stored_procedure.sql.jinja',
            ]

            for stencil in stencils:
                assert debug_output.find(stencil) != -1, \
                    f'stencil "{stencil}" not found in debug output'

        remove_file(debug_file)
        self.compare_directories(results['configuration'])
