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
from src.unittest.common import TestCommon

FIXTURE_DIR = pathlib.Path('src/unittest/') / 'tintin'


class TestTinTin(TestCommon):
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
    @pytest.mark.datafiles(FIXTURE_DIR / '1_global_variables')
    def test_global_variables(self, datafiles):
        global_namespace = '{"NO_cast": true}'

        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, datafiles / 'settings.json')

        # set up StempelWerk and execute full run
        self.run_and_compare(config_path, global_namespace=global_namespace)


    # After a year of intense testing, Tin Tin moved on to custom modules. He
    # wanted to call them "prison_cell" and "inmate_canteen", but the author of
    # StempelWerk put his foot down.
    @pytest.mark.datafiles(FIXTURE_DIR / '2_custom_module')
    def test_custom_module(self, datafiles):
        config = {
            'stencil_dir_name': 'stencils',
            'custom_modules': [
                'src.custom.add_filters',
                'src.custom.add_tests',
            ],
        }

        config_path = self.create_config(
            config, datafiles / 'settings.json')

        # set up StempelWerk and execute full run
        self.run_and_compare(config_path)


    # Only 148 years to go! At Tin Tin's current pace, he will run out of work
    # by the end of the century ...
    #
    # Anyway, he recently started testing Jinja extensions. We will keep you
    # posted on his progress. Don't expect news anytime soon, though.
    @pytest.mark.datafiles(FIXTURE_DIR / '3_jinja_extension')
    def test_jinja_extension(self, datafiles):

        def file_exists(file_path):
            if not file_path.is_file():
                raise FileNotFoundError(file_path)


        def remove_file(partial_file_path):
            output_path = datafiles / partial_file_path
            output_path.unlink()

        # ---------------------------------------------------------------------

        debug_path = datafiles / '20-output/Debug.txt'

        config = {
            'stencil_dir_name': 'stencils',
            'jinja_extensions': [
                'jinja2.ext.debug',
            ],
        }

        config_path = self.create_config(
            config, datafiles / 'settings.json')

        with pytest.raises(FileNotFoundError):
            file_exists(debug_path)

        # set up StempelWerk and execute full run
        results = self.run_with_config_file(config_path)

        file_exists(debug_path)

        debug_output = debug_path.read_text()
        print(debug_output)

        stencils = [
            '00-common_settings.sql.jinja',
            '10-sql_create_table.sql.jinja',
            '20-sql_create_stored_procedure.sql.jinja',
        ]

        for stencil in stencils:
            assert debug_output.find(stencil) != -1, \
                f'stencil "{stencil}" not found in debug output'

        remove_file(debug_path)
        self.compare_directories(results['configuration'])
