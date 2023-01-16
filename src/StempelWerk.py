#! /usr/bin/python3

# ----------------------------------------------------------------------------
#
#  StempelWerk
#  ===========
#  Automatic code generation from Jinja2 templates
#
#  Copyright (c) 2020-2023 Martin Zuther (https://www.mzuther.de/)
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions
#  are met:
#
#  1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
#  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
#  COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
#  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
#  OF THE POSSIBILITY OF SUCH DAMAGE.
#
#  Thank you for using free software!
#
# ----------------------------------------------------------------------------

import argparse
import copy
import dataclasses
import datetime
import importlib
import json
import math
import os
import pathlib
import platform
import stat
import sys

import jinja2
from .DirWalk.DirWalk import dirwalk


class StempelWerk:
    # ---------------------------------------------------------------------

    APPLICATION = 'StempelWerk'
    VERSION = '0.7.7'
    AUTHOR = 'Martin Zuther'
    DESCRIPTION = 'Automatic code generation from Jinja2 templates.'
    LICENSE = 'BSD 3-Clause License'

    APPLICATION_VERSION = f'{APPLICATION} v{VERSION}'
    COPYRIGHT = f'{APPLICATION_VERSION:20} (c) 2020-2023 {AUTHOR}'

    @staticmethod
    def format_version(verbosity=0):
        if verbosity < 0:
            return StempelWerk.APPLICATION_VERSION
        else:
            return (
                StempelWerk.COPYRIGHT + '\n' +
                f'Licensed under the {StempelWerk.LICENSE}'
            )

    @staticmethod
    def format_description(verbosity=0):
        return (
            StempelWerk.format_version(verbosity) + '\n\n' +
            StempelWerk.DESCRIPTION
        )

    def _display_version(self, verbosity=0):
        version_message = self.format_version(verbosity)

        print()
        if verbosity < 0:
            print(version_message)
        else:
            for line in version_message.split('\n'):
                print(f'[ {line:<48} ]')
        print()

    # ---------------------------------------------------------------------

    @staticmethod
    def _print_context(context, message):
        if message:
            message = f'{context}: {message}'
        print(message)


    @staticmethod
    def _print_error(message=''):
        StempelWerk._print_context('ERROR', message)


    @staticmethod
    def _print_debug(verbosity, message=''):
        if verbosity > 0:
            StempelWerk._print_context('DEBUG', message)


    def print_error(self, message=''):
        self._print_error(message)


    def print_debug(self, message=''):
        self._print_debug(self.settings.verbosity, message)

    # ---------------------------------------------------------------------

    # Auto-create settings class to write leaner code
    #
    # The "@dataclass" decorator creates a class, class members, and a
    # constructor with key-word parameters that have default values.
    #
    # In addition, this allows us to address settings with the more
    # readable membership operator ("settings.template_dir") instead
    # of using dictionary access ("settings['template_dir']").
    @dataclasses.dataclass
    class Settings:
        root_dir: str
        template_dir: str
        output_dir: str
        stencil_dir_name: str
        included_file_extensions: list
        # ----------------------------------------
        process_only_modified: bool
        verbosity: int = 0
        # ----------------------------------------
        jinja_options: list = dataclasses.field(
            default_factory=dict)
        jinja_extensions: list = dataclasses.field(
            default_factory=list)
        custom_modules: list = dataclasses.field(
            default_factory=list)
        # ----------------------------------------
        last_run_file: str = '.last_run'
        marker_new_file: str = '### New file:'
        marker_content: str = '### Content:'

        @staticmethod
        def finalize_path(root_dir, original_path):
            original_path = original_path.strip()

            new_path = os.path.join(root_dir, original_path)
            new_path = os.path.normpath(new_path)

            return new_path


        def __post_init__(self):
            # root directory is relative to the location of this file
            script_dir = os.path.dirname(os.path.abspath(__file__))

            self.root_dir = self.finalize_path(
                script_dir, self.root_dir)

            # all other paths are relative to the root directory
            self.template_dir = self.finalize_path(
                self.root_dir,
                self.template_dir)

            # automatically create template folder
            #
            # NOTE: "os.makedirs" expects normalized paths
            os.makedirs(self.template_dir, exist_ok=True)

            self.output_dir = self.finalize_path(
                self.root_dir, self.output_dir)

            # automatically create output folder
            #
            # NOTE: "os.makedirs" expects normalized paths
            os.makedirs(self.output_dir, exist_ok=True)

            self.last_run_file = self.finalize_path(
                self.root_dir, self.last_run_file)

    # ---------------------------------------------------------------------

    # Template class for customizing the Jinja environment
    class CustomCodeTemplate:  # noqa: E301
        def __init__(self, copy_of_settings):
            # this is only a copy; changing this variable does *not*
            # change the settings of StempelWerk
            self.settings = copy_of_settings

        def update_environment(self, jinja_environment):
            return jinja_environment

        def print_error(self, message=''):
            StempelWerk._print_error(message)

        def print_debug(self, message=''):
            StempelWerk._print_debug(self.settings.verbosity, message)

    # ---------------------------------------------------------------------

    def __init__(self, command_line_arguments):
        args = self.parse_command_line(command_line_arguments)

        self._display_version(args.verbosity)

        self.load_settings(
            args.config_file_path,
            args.verbosity,
            args.process_only_modified)


    def parse_command_line(self, command_line_arguments):
        class HelpfulArgumentParser(argparse.ArgumentParser):
            def exit(self, status=0, message=None):
                if status:
                    # display help on errors without showing usage message twice
                    help_message = self.format_help()
                    help_message = help_message.replace(self.format_usage(), '')
                    print(help_message, file=sys.stderr)

                # resume default processing
                super().exit(status, message)

        parser = HelpfulArgumentParser(
            description=self.format_description(),
            formatter_class=argparse.RawDescriptionHelpFormatter)

        parser.add_argument(
            '-V',
            '--version',
            action='version',
            version=self.APPLICATION_VERSION)

        parser.add_argument(
            '-m',
            '--only-modified',
            action='store_true',
            help='only process modified templates',
            dest='process_only_modified')

        verbosity_group = parser.add_mutually_exclusive_group()

        verbosity_group.add_argument(
            '-qq',
            '--ultraquiet',
            action='store_const',
            const=-2,
            default=0,
            help='display minimal output',
            dest='verbosity')

        verbosity_group.add_argument(
            '-q',
            '--quiet',
            action='store_const',
            const=-1,
            default=0,
            help='display less output',
            dest='verbosity')

        verbosity_group.add_argument(
            '-v',
            '--verbose',
            action='store_const',
            const=1,
            default=0,
            help='display more output and include debug information',
            dest='verbosity')

        parser.add_argument(
            'config_file_path',
            help='path to JSON file containing configuration',
            metavar='CONFIG_FILE')

        cla_without_scriptname = command_line_arguments[1:]
        args = parser.parse_args(cla_without_scriptname)
        return args


    def load_settings(self, config_file_path, verbosity, process_only_modified):
        # ... except for the path of the configuration file, which is
        # relative to the current working directory
        config_file_path = self.Settings.finalize_path(
            '', config_file_path)

        try:
            with open(config_file_path) as f:
                loaded_settings = json.load(f)

        except FileNotFoundError:
            self.print_error(f'File "{config_file_path}" not found.')
            self.print_error()
            exit(1)

        except json.decoder.JSONDecodeError as err:
            self.print_error(f'File "{config_file_path}" is broken:')
            self.print_error(f'{err}')
            self.print_error()
            exit(1)

        except TypeError as err:
            self.print_error('Did you provide all settings in'
                             f'"{config_file_path}"?')
            self.print_error(f'{err}')
            self.print_error()

            # print traceback to help with debugging
            raise err

        # add settings from command line (or overwrite if
        # specified in JSON)
        loaded_settings['verbosity'] = verbosity
        loaded_settings['process_only_modified'] = process_only_modified

        # here's where the magic happens: unpack JSON file into class
        self.settings = self.Settings(**loaded_settings)


    def create_environment(self):
        self.print_debug('Loading templates ...')

        # NOTE: Jinja loads templates from sub-directories;
        # NOTE: stencils will also be included
        template_loader = jinja2.FileSystemLoader(
            # cache stencils and templates to improve performance
            self.settings.template_dir)

        self.jinja_environment = jinja2.Environment(
            loader=template_loader,
            **self.settings.jinja_options)

        template_filenames = self.jinja_environment.list_templates()

        if not template_filenames:
            self.print_error()
            self.print_error('No templates found.')
            self.print_error()
            exit(1)

        stencil_filenames = []
        for stencil_filename in template_filenames:
            path_components = os.path.split(stencil_filename)
            if self.settings.stencil_dir_name in path_components:
                stencil_filenames.append(stencil_filename)

        # display warning and continue processing (some people might
        # not want to use stencils)
        if not stencil_filenames:
            self.print_error()
            self.print_error('No stencils found.')
            self.print_error()
        # list all templates in cache
        elif self.settings.verbosity > 0:
            self.print_debug(' ')
            self.print_debug('Available stencils:')
            self.print_debug(' ')

            for stencil_filename in stencil_filenames:
                self.print_debug(f'  - {stencil_filename}')

            self.print_debug(' ')
            self.print_debug('  Use relative paths to access templates in'
                             'sub-directories')
            self.print_debug('  (https://stackoverflow.com/a/9644828).')
            self.print_debug(' ')

        self.print_debug('Done.')
        self.print_debug()

        # load extensions and run custom Python code
        self._update_environment()


    def _update_environment(self):
        # load Jinja extensions first so they can be referenced in custom
        # Python code
        if self.settings.jinja_extensions:
            self.print_debug('Loading extensions:')
            self.print_debug(' ')

            for extension in self.settings.jinja_extensions:
                self.print_debug(f'  - {extension}')
                self.jinja_environment.add_extension(extension)

            self.print_debug(' ')
            self.print_debug('Done.')
            self.print_debug()

        # run custom Python code
        if self.settings.custom_modules:
            self.print_debug('Loading custom modules:')
            self.print_debug(' ')

            for module_name in self.settings.custom_modules:
                self.print_debug(f'  [ {module_name} ]')

                # import code as module
                module_spec = importlib.util.find_spec(
                    module_name)
                imported_module = importlib.util.module_from_spec(
                    module_spec)

                # execute module its own namespace
                module_spec.loader.exec_module(
                    imported_module)

                # prevent changes to settings
                custom_code = imported_module.CustomCode(
                    copy.deepcopy(self.settings))

                self.print_debug('  - Updating environment ...')

                # execute custom code and store updated Jinja environment
                self.jinja_environment = custom_code.update_environment(
                    self.jinja_environment)

                self.print_debug('  - Done.')
                self.print_debug(' ')

            self.print_debug('Done.')
            self.print_debug()


    def render_template(self, template_filename, processed_templates=0,
                        saved_files=0):
        # create environment automatically
        if not hasattr(self, 'jinja_environment'):
            self.create_environment()

        template_filename = os.path.relpath(
            template_filename, self.settings.template_dir)

        processed_templates += 1

        if self.settings.verbosity < -1:
            print('.', end='')

            if (processed_templates % 40) == 0:
                print()
            elif (processed_templates % 10) == 0:
                print(' ', end='')
        elif self.settings.verbosity >= -1:
            print('- {}'.format(template_filename))

        # Jinja2 cannot handle Windows paths
        if os.path.sep != '/':
            template_filename = template_filename.replace(os.path.sep, '/')

        # render template
        try:
            template = self.jinja_environment.get_template(template_filename)
            content_of_multiple_files = template.render()

        except (jinja2.exceptions.TemplateSyntaxError,
                jinja2.exceptions.TemplateAssertionError) as err:
            self.print_error()

            if self.settings.verbosity < -1:
                self.print_error()
                self.print_error(f'in file "{template_filename}"')

            self.print_error(f'{err.message} (line {err.lineno})')
            self.print_error()

            raise(err)

        except Exception as err:
            if self.settings.verbosity < -1:
                self.print_error()
                self.print_error()
                self.print_error(f'in file "{template_filename}"')

            self.print_error()

            raise(err)

        # split content of multiple files
        split_contents = content_of_multiple_files.split(
            self.settings.marker_new_file)

        for content_of_single_file in split_contents:
            saved_files += self._render_to_single_file(content_of_single_file)

        if self.settings.verbosity >= 0:
            print()

        return (processed_templates, saved_files)


    def _render_to_single_file(self, content_of_single_file):
        # content starts with "marker_new_file", so first string is
        # empty (or contains whitespace when a template is not well
        # written)
        if not content_of_single_file.strip():
            return 0

        # extract path and content of output file
        output_filename, content = content_of_single_file.split(
            self.settings.marker_content, 1)

        # FIXME: check validity of input
        output_filename = output_filename.strip()
        content = content.lstrip()

        output_filename = self.Settings.finalize_path(
            self.settings.output_dir, output_filename)

        _, file_extension = os.path.splitext(output_filename)

        if self.settings.verbosity >= 0:
            print('  - {}'.format(os.path.relpath(
                output_filename, self.settings.output_dir)))

        # use default line ending of system
        newline = None

        # but ensure Batch files use Windows line endings, otherwise
        # seemingly random lines will be executed
        if file_extension == '.bat':
            newline = '\r\n'

        # Jinja2 encodes all strings in UTF-8
        with open(output_filename, mode='w', encoding='utf-8',
                  newline=newline) as f:
            f.write(content)

        # make Linux shell files executable by owner
        if file_extension == '.sh' and platform.system() == 'Linux':
            with pathlib.Path(output_filename) as f:
                mode = f.stat().st_mode
                f.chmod(mode | stat.S_IXUSR)

        return 1


    def process_templates(self, process_only_modified=None):
        # use default if argument was not specified
        if process_only_modified is None:
            process_only_modified = self.settings.process_only_modified

        start_of_processing = datetime.datetime.now()

        dirwalk_inclusions = {
            'excluded_directory_names': [
                # do not render stencils
                self.settings.stencil_dir_name
            ],
            'excluded_file_names': [],
            'included_file_extensions': self.settings.included_file_extensions,
        }

        modified_after = None
        if process_only_modified:
            # get time of last run
            try:
                with open(self.settings.last_run_file) as f:
                    modified_after = f.read()
                    modified_after = modified_after.strip()
            except IOError:
                modified_after = None

        # find all Jinja2 files in template directory
        template_filenames = dirwalk(self.settings.template_dir,
                                     included=dirwalk_inclusions,
                                     modified_after=modified_after)

        # only save time of current run when files are processed
        if template_filenames:
            processed = 0
            saved = 0

            for template_filename in template_filenames:
                processed, saved = self.render_template(template_filename,
                                                        processed, saved)

            # save time of current run
            with open(self.settings.last_run_file, mode='w') as f:
                # convert to UNIX time
                start_of_processing_timestamp = start_of_processing.timestamp()

                # round down to ensure that files with inaccurate timestamps and
                # other edge cases are included
                start_of_processing_timestamp = math.floor(
                    start_of_processing_timestamp)

                f.write(str(start_of_processing_timestamp))

            processing_time = datetime.datetime.now() - start_of_processing
            time_per_template = processing_time / processed
            time_per_file = processing_time / saved

            self.print_debug(f'Time per template file: {time_per_template}')
            self.print_debug(f'Time per output file:   {time_per_file}')
            self.print_debug()

            if self.settings.verbosity < 0:
                print()

                if self.settings.verbosity < -1 and (processed % 40) != 0:
                    print()

                print(f'{processed} => {saved} in {processing_time}')
                print()
            else:
                print(f'TOTAL: {processed} templates => {saved} files',
                      f'in {processing_time}')
                print()


if __name__ == '__main__':
    sw = StempelWerk(sys.argv)
    sw.process_templates()
