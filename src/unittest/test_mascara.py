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

FIXTURE_DIR = pathlib.Path('src/unittest/') / 'mascara'


class TestMascara(TestCommon):
    # Mascara is a front-end developer wanting to learn coding. From her
    # previous experience, she thinks that getting an existing Python
    # application to do what she wants is already coding. She's a good tester,
    # so we'll let someone else break the bad news to her ...
    #
    # After getting StempelWerk to run (congrats!), Mascara randomly deletes and
    # changes files and checks whether the application restores the files.
    @pytest.mark.datafiles(FIXTURE_DIR / '1_process_only_modified_1')
    def test_process_only_modified_1(self, datafiles):

        def convenience_run(partial_run, matching):
            results = self.run(
                config_path,
                process_only_modified=partial_run)

            if matching:
                self.compare_directories(config)
            else:
                with pytest.raises(AssertionError):
                    self.compare_directories(config)

            return results

        # ---------------------------------------------------------------------

        custom_config = {
            'stencil_dir_name': 'stencils',
        }

        # set up StempelWerk and execute full run
        config_path = datafiles / 'settings.json'
        results = self.run_and_compare(custom_config, config_path)

        config = results['configuration']
        assert results['saved_files'] == 2

        # full run renders all files unconditonally
        file_to_be_deleted = datafiles / '20-output/ab.txt'
        file_to_be_deleted.unlink()

        file_to_be_modified = datafiles / '20-output/cd.txt'
        self.modify_file(config, file_to_be_modified)

        results = convenience_run(partial_run=False, matching=True)
        assert results['saved_files'] == 2

        # partial run leaves deleted output file alone
        file_to_be_deleted = datafiles / '20-output/cd.txt'
        file_to_be_deleted.unlink()

        results = convenience_run(partial_run=True, matching=False)
        assert results['saved_files'] == 0

        # full run re-creates all output files
        results = convenience_run(partial_run=False, matching=True)
        assert results['saved_files'] == 2

        # partial run does not render externally modified output file
        file_to_be_modified = datafiles / '20-output/ab.txt'
        self.modify_file(config, file_to_be_modified)

        results = convenience_run(partial_run=True, matching=False)
        assert results['saved_files'] == 0

        # full run also renders externally modified output files
        results = convenience_run(partial_run=False, matching=True)
        assert results['saved_files'] == 2


    # She updates a template and checks whether a partial run updates the
    # respective output file.
    @pytest.mark.datafiles(FIXTURE_DIR / '1_process_only_modified_2')
    def test_process_only_modified_2(self, datafiles):

        def convenience_run(partial_run, matching):
            results = self.run(
                config_path,
                process_only_modified=partial_run)

            if matching:
                self.compare_directories(config)
            else:
                with pytest.raises(AssertionError):
                    self.compare_directories(config)

            return results

        # ---------------------------------------------------------------------

        custom_config = {
            'stencil_dir_name': 'stencils',
        }

        # set up StempelWerk and execute full run
        config_path = datafiles / 'settings.json'
        results = self.run_and_compare(custom_config, config_path)

        config = results['configuration']
        assert results['saved_files'] == 2

        # partial run does not update changed files
        self.update_file(datafiles / '30-expected_updated/ab.txt')

        results = convenience_run(partial_run=True, matching=False)
        assert results['saved_files'] == 0

        # partial run updates output files of changed templates
        self.update_file(datafiles / '10-templates_updated/ab.jinja')

        results = convenience_run(partial_run=True, matching=True)
        assert results['saved_files'] == 1


    # Having the genes of a real tester, Mascara checks whether updating a
    # stencil changes any output files in a partial run.
    @pytest.mark.datafiles(FIXTURE_DIR / '1_process_only_modified_3')
    def test_process_only_modified_3(self, datafiles):

        def convenience_run(partial_run, matching):
            results = self.run(
                config_path,
                process_only_modified=partial_run)

            if matching:
                self.compare_directories(config)
            else:
                with pytest.raises(AssertionError):
                    self.compare_directories(config)

            return results

        # ---------------------------------------------------------------------

        custom_config = {
            'stencil_dir_name': 'stencils',
        }

        # set up StempelWerk and execute full run
        config_path = datafiles / 'settings.json'
        results = self.run_and_compare(custom_config, config_path)

        config = results['configuration']
        assert results['saved_files'] == 2

        # partial run does not check for changed stencils
        self.update_file(
            datafiles / '10-templates_updated/stencils/common.jinja')

        results = convenience_run(partial_run=True, matching=True)
        assert results['saved_files'] == 0

        # full run applies changed stencils
        self.update_file(datafiles / '30-expected_updated/ab.txt')
        self.update_file(datafiles / '30-expected_updated/cd.txt')

        results = convenience_run(partial_run=False, matching=True)
        assert results['saved_files'] == 2


    # Mascara wants to become more proficient in Python [ahem] and checks
    # whether StempelWerk is really as lean as its developer promises.
    @pytest.mark.datafiles(FIXTURE_DIR / '1_process_only_modified_1')
    def test_lean_template_removal(self, datafiles):

        def convenience_run(partial_run, matching):
            results = self.run(
                config_path,
                process_only_modified=partial_run)

            if matching:
                self.compare_directories(config)
            else:
                with pytest.raises(AssertionError):
                    self.compare_directories(config)

            return results

        # ---------------------------------------------------------------------

        custom_config = {
            'stencil_dir_name': 'stencils',
        }

        # set up StempelWerk and execute full run
        config_path = datafiles / 'settings.json'
        results = self.run_and_compare(custom_config, config_path)

        config = results['configuration']
        assert results['saved_files'] == 2

        # deleting a template leaves the output file alone
        file_to_be_deleted = datafiles / '10-templates/ab.jinja'
        file_to_be_deleted.unlink()

        results = convenience_run(partial_run=False, matching=True)
        assert results['saved_files'] == 1


    # After having become a Python goddess, she wants to start a hacking career.
    # And what do hackers do? Delete files. Yes! YES!!!
    #
    # "rm -rf /proc/" looks tempting, but Mascara wants to show off her Python
    # skills. She thus deletes a file that StempelWerk creates during runtime.
    # With little effect - StempelWerk just creates it again. No! NO!!!
    @pytest.mark.datafiles(FIXTURE_DIR / '1_process_only_modified_1')
    def test_last_run_file(self, datafiles):

        def convenience_run(partial_run, matching):
            results = self.run(
                config_path,
                process_only_modified=partial_run)

            if matching:
                self.compare_directories(config)
            else:
                with pytest.raises(AssertionError):
                    self.compare_directories(config)

            return results

        # ---------------------------------------------------------------------

        last_run_file = datafiles / 'mascara.HACK'

        custom_config = {
            'stencil_dir_name': 'stencils',
            'last_run_file': str(last_run_file),
        }

        assert not last_run_file.is_file()

        # set up StempelWerk and execute full run
        config_path = datafiles / 'settings.json'
        results = self.run_and_compare(custom_config, config_path)

        config = results['configuration']
        assert results['saved_files'] == 2

        # "last_run_file" is created
        assert last_run_file.is_file()

        # partial run finds "last_run_file" and does not render any files
        results = convenience_run(partial_run=True, matching=True)
        assert results['saved_files'] == 0

        # "last_run_file" is not deleted accidentally
        assert last_run_file.is_file()

        # partial run becomes full run when "last_run_file" is missing
        last_run_file.unlink()

        results = convenience_run(partial_run=True, matching=True)
        assert results['saved_files'] == 2

        # "last_run_file" is re-created
        assert last_run_file.is_file()
