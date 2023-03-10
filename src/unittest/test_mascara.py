# The story, all names, characters, and incidents portrayed in this test are
# fictitious. No identification with actual persons (living or deceased),
# places, buildings, and products is intended or should be inferred.
#
# In other words: I have great and helpful colleagues with a lot of humour. In
# order to make writing these tests more fun, I have used their (obfuscated)
# names, but all personality traits have been made up. I hope they have as much
# fun reading these tests as I had in writing them!

import os
import shutil

import pytest
from src.unittest.common import TestCommon


class TestMascara(TestCommon):
    def run_with_config_file(self, config_path, unit_test_directory,
                             global_namespace=None):
        unit_test_path = os.path.join(
            './src/unittest/mascara/',
            unit_test_directory)

        return super().run_with_config_file(
            config_path,
            unit_test_path,
            global_namespace=global_namespace)

    # ---------------------------------------------------------------------

    # Mascara is a front-end developer wanting to learn coding. From her
    # previous experience, she thinks that getting an existing Python
    # application to do what she wants is already coding. She's a good tester,
    # so we'll let someone else break the bad news to her ...
    #
    # After getting StempelWerk to run (congrats!), Mascara randomly deletes and
    # changes files and checks whether the application restores the files.
    def test_process_only_modified_1(self, tmp_path):

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

        unit_test_directory = '1_process_only_modified_1'

        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        # set up StempelWerk and execute full run
        results = self.run_and_compare(config_path, unit_test_directory)
        config = results['configuration']
        assert results['saved_files'] == 2

        # full run renders all files unconditonally
        remove_file('20-output/ab.txt')
        modify_file('20-output/cd.txt')
        results = convenience_run(partial_run=False, matching=True)
        assert results['saved_files'] == 2

        # partial run leaves deleted output file alone
        remove_file('20-output/cd.txt')
        results = convenience_run(partial_run=True, matching=False)
        assert results['saved_files'] == 0

        # full run re-creates all output files
        results = convenience_run(partial_run=False, matching=True)
        assert results['saved_files'] == 2

        # partial run does not render externally modified output file
        modify_file('20-output/ab.txt')
        results = convenience_run(partial_run=True, matching=False)
        assert results['saved_files'] == 0

        # full run also renders externally modified output files
        results = convenience_run(partial_run=False, matching=True)
        assert results['saved_files'] == 2


    # She updates a template and checks whether a partial run updates the
    # respective output file.
    def test_process_only_modified_2(self, tmp_path):

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


        def update_file(partial_file_path):
            input_path = os.path.join(tmp_path, partial_file_path)
            output_path = input_path.replace('_updated', '')

            shutil.copyfile(input_path, output_path)

        # ---------------------------------------------------------------------

        unit_test_directory = '1_process_only_modified_2'

        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        # set up StempelWerk and execute full run
        results = self.run_and_compare(config_path, unit_test_directory)
        config = results['configuration']
        assert results['saved_files'] == 2

        update_file('30-expected_updated/ab.txt')

        # partial run does not update changed files
        results = convenience_run(partial_run=True, matching=False)
        assert results['saved_files'] == 0

        update_file('10-templates_updated/ab.jinja')

        # partial run updates output files of changed templates
        results = convenience_run(partial_run=True, matching=True)
        assert results['saved_files'] == 1


    # Having the genes of a real tester, Mascara checks whether updating a
    # stencil changes any output files in a partial run.
    def test_process_only_modified_3(self, tmp_path):

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


        def update_file(partial_file_path):
            input_path = os.path.join(tmp_path, partial_file_path)
            output_path = input_path.replace('_updated', '')

            shutil.copyfile(input_path, output_path)

        # ---------------------------------------------------------------------

        unit_test_directory = '1_process_only_modified_3'

        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        # set up StempelWerk and execute full run
        results = self.run_and_compare(config_path, unit_test_directory)
        config = results['configuration']
        assert results['saved_files'] == 2

        update_file('10-templates_updated/stencils/common.jinja')

        # partial run does not check for changed stencils
        results = convenience_run(partial_run=True, matching=True)
        assert results['saved_files'] == 0

        update_file('30-expected_updated/ab.txt')
        update_file('30-expected_updated/cd.txt')

        # full run applies changed stencils
        results = convenience_run(partial_run=False, matching=True)
        assert results['saved_files'] == 2


    # Mascara wants to get become more proficient in Python [ahem] and checks
    # whether StempelWerk is really as lean as its developer promises.
    def test_lean_template_removal(self, tmp_path):

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


        def remove_file(partial_file_path):
            output_path = os.path.join(tmp_path, partial_file_path)
            os.remove(output_path)

        # ---------------------------------------------------------------------

        unit_test_directory = '1_process_only_modified_1'

        config = {
            'stencil_dir_name': 'stencils',
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        # set up StempelWerk and execute full run
        results = self.run_and_compare(config_path, unit_test_directory)
        config = results['configuration']
        assert results['saved_files'] == 2

        # deleting a template leaves the output file alone
        remove_file('10-templates/ab.jinja')
        results = convenience_run(partial_run=False, matching=True)
        assert results['saved_files'] == 1


    # After having become a Python goddess, she wants to start a hacking career.
    # And what do hackers do? Delete files. Yes! YES!!!
    #
    # "rm -rf /proc/" looks tempting, but Mascara wants to show off her Python
    # skills. She thus deletes a file that StempelWerk creates during runtime.
    # With little effect - StempelWerk just creates it again. No! NO!!!
    def test_last_run_file(self, tmp_path):

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


        def file_exists(partial_file_path):
            file_path = os.path.join(tmp_path, partial_file_path)
            if not os.path.isfile(file_path):
                raise FileNotFoundError(file_path)


        def remove_file(partial_file_path):
            output_path = os.path.join(tmp_path, partial_file_path)
            os.remove(output_path)

        # ---------------------------------------------------------------------

        unit_test_directory = '1_process_only_modified_1'

        last_run_file = 'mascara.HACK'

        config = {
            'stencil_dir_name': 'stencils',
            'last_run_file': last_run_file,
        }

        config_path = self.create_config(
            config, tmp_path, 'settings.json')

        with pytest.raises(FileNotFoundError):
            file_exists(last_run_file)

        # set up StempelWerk and execute full run
        results = self.run_and_compare(config_path, unit_test_directory)
        config = results['configuration']
        assert results['saved_files'] == 2

        # "last_run_file" is created
        file_exists(last_run_file)

        # partial run finds "last_run_file" and does not render any files
        results = convenience_run(partial_run=True, matching=True)
        assert results['saved_files'] == 0

        # "last_run_file" is not deleted accidentally
        file_exists(last_run_file)

        # partial run becomes full run when "last_run_file" is missing
        remove_file(last_run_file)
        results = convenience_run(partial_run=True, matching=True)
        assert results['saved_files'] == 2

        # "last_run_file" is re-created
        file_exists(last_run_file)