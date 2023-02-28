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
    VERSION = '0.8.4'
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

    class LinePrinter:
        def __init__(self, verbosity):
            self.verbosity = verbosity


        def _print_context(self, context, message):
            if message:
                message = f'{context}: {message}'
            print(message)


        def error(self, message=''):
            self._print_context('ERROR', message)


        def debug(self, message=''):
            if self.verbosity > 0:
                self._print_context('DEBUG', message)

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
        # ----------------------------------------
        included_file_extensions: list
        stencil_dir_name: str = ''
        create_directories: bool = False
        # ----------------------------------------
        global_namespace: list = dataclasses.field(
            default_factory=dict)
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
        def __init__(self, copy_of_settings, printer):
            # this is only a copy; changing this variable does *not*
            # change the settings of StempelWerk
            self.settings = copy_of_settings
            self.printer = printer

        def update_environment(self, jinja_environment):
            return jinja_environment

        def print_error(self, message=''):
            self.printer.error(message)

        def print_debug(self, message=''):
            self.printer.debug(message)

    # ---------------------------------------------------------------------

    class CommandLineParser:
        @property
        def parser(self):
            class HelpfulArgumentParser(argparse.ArgumentParser):
                def exit(self, status=0, message=None):
                    if status:
                        # display help on errors without showing usage message
                        # twice
                        help_message = self.format_help()
                        help_message = help_message.replace(
                            self.format_usage(),
                            '')
                        print(help_message, file=sys.stderr)

                    # resume default processing
                    super().exit(status, message)

            parser = HelpfulArgumentParser(
                description=StempelWerk.format_description(),
                formatter_class=argparse.RawDescriptionHelpFormatter)

            parser.add_argument(
                '-V',
                '--version',
                action='version',
                version=StempelWerk.APPLICATION_VERSION)

            parser.add_argument(
                '-m',
                '--only-modified',
                action='store_true',
                help='only process modified templates',
                dest='process_only_modified')

            parser.add_argument(
                '-g',
                '--globals',
                action='store',
                help='string or file containing JSON-formatted global variables',
                metavar='JSON',
                dest='global_namespace')

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

            return parser


        def __init__(self, command_line_arguments):
            cla_without_scriptname = command_line_arguments[1:]
            args = self.parser.parse_args(cla_without_scriptname)

            self.printer = StempelWerk.LinePrinter(args.verbosity)

            # all paths are relative to the root directory, except for the path
            # of the configuration file, which is relative to the current
            # working directory
            config_file_path = StempelWerk.Settings.finalize_path(
                '', args.config_file_path)

            # parse config file
            loaded_settings = self.load_json_file(config_file_path)

            # parse global variables for Jinja environment
            #
            # provide default global namespace
            if args.global_namespace is None:
                loaded_settings['global_namespace'] = {}
            # parse JSON-formatted dictionary
            elif args.global_namespace.strip().startswith('{'):
                loaded_settings['global_namespace'] = json.loads(
                    args.global_namespace)
            # load JSON file
            else:
                loaded_settings['global_namespace'] = self.load_json_file(
                    args.global_namespace)

            # here's where the magic happens: unpack JSON file into class
            self.settings = StempelWerk.Settings(**loaded_settings)

            # store settings that may be overwritten at runtime separately
            self.process_only_modified = args.process_only_modified
            self.verbosity = args.verbosity


        def load_json_file(self, json_file_path):
            try:
                with open(json_file_path) as f:
                    result = json.load(f)

            except FileNotFoundError:
                self.printer.error(f'File "{json_file_path}" not found.')
                self.printer.error()
                exit(1)

            except json.decoder.JSONDecodeError as err:
                self.printer.error(f'File "{json_file_path}" is broken:')
                self.printer.error(f'{err}')
                self.printer.error()
                exit(1)

            except TypeError as err:
                self.printer.error('Did you provide all settings in'
                                   f'"{json_file_path}"?')
                self.printer.error(f'{err}')
                self.printer.error()

                # print traceback to help with debugging
                raise err

            return result

    # ---------------------------------------------------------------------

    def __init__(self, settings, verbosity=0):
        self.settings = settings

        self.verbosity = verbosity
        self.printer = self.LinePrinter(self.verbosity)
        self._display_version(self.verbosity)


    def create_environment(self):
        self.printer.debug('Loading templates ...')

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
            self.printer.error()
            self.printer.error('No templates found.')
            self.printer.error()
            exit(1)

        stencil_filenames = []
        for stencil_filename in template_filenames:
            path_components = os.path.split(stencil_filename)
            if self.settings.stencil_dir_name in path_components:
                stencil_filenames.append(stencil_filename)

        # check whether stencil directories contain any stencils
        if self.settings.stencil_dir_name and not stencil_filenames:
            self.printer.error()
            self.printer.error('No stencils found.')
            self.printer.error()
            exit(1)

        # list all templates in cache
        if self.verbosity > 0:
            self.printer.debug(' ')
            self.printer.debug('Available stencils:')
            self.printer.debug(' ')

            for stencil_filename in stencil_filenames:
                self.printer.debug(f'  - {stencil_filename}')

            self.printer.debug(' ')
            self.printer.debug('  Use relative paths to access templates in'
                               'sub-directories')
            self.printer.debug('  (https://stackoverflow.com/a/9644828).')
            self.printer.debug(' ')

        self.printer.debug('Done.')
        self.printer.debug()

        # load extensions and run custom Python code
        self._update_environment()


    def _update_environment(self):
        # load Jinja extensions first so they can be referenced in custom
        # Python code
        if self.settings.jinja_extensions:
            self.printer.debug('Loading extensions:')
            self.printer.debug(' ')

            for extension in self.settings.jinja_extensions:
                self.printer.debug(f'  - {extension}')
                self.jinja_environment.add_extension(extension)

            self.printer.debug(' ')
            self.printer.debug('Done.')
            self.printer.debug()

        # run custom Python code
        if self.settings.custom_modules:
            self.printer.debug('Loading custom modules:')
            self.printer.debug(' ')

            for module_name in self.settings.custom_modules:
                self.printer.debug(f'  [ {module_name} ]')

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
                    copy.deepcopy(self.settings),
                    self.printer)

                self.printer.debug('  - Updating environment ...')

                # execute custom code and store updated Jinja environment
                self.jinja_environment = custom_code.update_environment(
                    self.jinja_environment)

                self.printer.debug('  - Done.')
                self.printer.debug(' ')

            self.printer.debug('Done.')
            self.printer.debug()


    def render_template(self, template_filename, global_namespace=None):
        # create environment automatically
        if not hasattr(self, 'jinja_environment'):
            self.create_environment()

        template_filename = os.path.relpath(
            template_filename, self.settings.template_dir)

        processed_templates = 1
        saved_files = 0

        if self.verbosity < -1:
            print('.', end='')

            if (processed_templates % 40) == 0:
                print()
            elif (processed_templates % 10) == 0:
                print(' ', end='')
        elif self.verbosity >= -1:
            print('- {}'.format(template_filename))

        # Jinja2 cannot handle Windows paths
        if os.path.sep != '/':
            template_filename = template_filename.replace(os.path.sep, '/')

        current_global_namespace = self.settings.global_namespace

        # add provided global variables, overwriting existing entries
        if global_namespace:
            current_global_namespace.update(global_namespace)

        # group global variables under key "globals" to explicitly
        # mark them as globals in code
        current_global_namespace = {
            'globals': current_global_namespace
        }

        # render template
        try:
            template = self.jinja_environment.get_template(
                template_filename,
                globals=current_global_namespace)

            content_of_multiple_files = template.render()

        except (jinja2.exceptions.TemplateSyntaxError,
                jinja2.exceptions.TemplateAssertionError) as err:
            self.printer.error()

            if self.verbosity < -1:
                self.printer.error()
                self.printer.error(f'in file "{template_filename}"')

            self.printer.error(f'{err.message} (line {err.lineno})')
            self.printer.error()

            raise(err)

        except Exception as err:
            if self.verbosity < -1:
                self.printer.error()
                self.printer.error()
                self.printer.error(f'in file "{template_filename}"')

            self.printer.error()

            raise(err)

        # split content of multiple files
        split_contents = content_of_multiple_files.split(
            self.settings.marker_new_file)

        for content_of_single_file in split_contents:
            saved_files += self._render_to_single_file(content_of_single_file)

        if self.verbosity >= 0:
            print()

        return (processed_templates, saved_files)


    def _render_to_single_file(self, content_raw):
        # content starts with "marker_new_file", so first string is
        # empty (or contains whitespace when a template is not well
        # written)
        if not content_raw.strip():
            return 0

        # catch problems with file separation markers early
        if (content_raw.count(self.settings.marker_new_file) != 0) or \
           (content_raw.count(self.settings.marker_content) != 1):
            self.printer.error(
                'there was a problem with splitting the output into files,')
            self.printer.error(
                'check "marker_new_file", "marker_content" and your templates.')
            self.printer.error()
            exit(1)

        # extract path and content of output file
        output_filename, content = content_raw.split(
            self.settings.marker_content, 1)

        # FIXME: check validity of input
        output_filename = output_filename.strip()
        content = content.lstrip()

        output_filename = self.Settings.finalize_path(
            self.settings.output_dir, output_filename)
        output_directory = os.path.dirname(output_filename)

        if not os.path.exists(output_directory):
            if self.settings.create_directories:
                os.makedirs(output_directory)
                if self.verbosity >= 0:
                    print(f'  - created directory "{output_directory}"')
            else:
                self.printer.error(
                    f'directory "{output_directory}"')
                self.printer.error(
                    'does not exist.')
                self.printer.error()
                exit(1)

        _, file_extension = os.path.splitext(output_filename)

        if self.verbosity >= 0:
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


    def process_templates(self, process_only_modified=False,
                          global_namespace=None):
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

        processed_templates = 0
        saved_files = 0

        # only save time of _templates current run when files are processed
        if template_filenames:
            for template_filename in template_filenames:
                processed, saved = self.render_template(
                    template_filename, global_namespace)

                processed_templates += processed
                saved_files += saved

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
            time_per_template = processing_time / processed_templates
            time_per_file = processing_time / saved_files

            self.printer.debug(f'Time per template file: {time_per_template}')
            self.printer.debug(f'Time per output file:   {time_per_file}')
            self.printer.debug()

            if self.verbosity < 0:
                print()

                if self.verbosity < -1 and (processed_templates % 40) != 0:
                    print()

                print(f'{processed_templates } =>',
                      f'{saved_files} in {processing_time}')
                print()
            else:
                print(f'TOTAL: {processed_templates } templates =>',
                      f'{saved_files} files in {processing_time}')
                print()

        return (processed_templates, saved_files)


if __name__ == '__main__':
    command_line_arguments = sys.argv
    parsed_args = StempelWerk.CommandLineParser(command_line_arguments)

    sw = StempelWerk(parsed_args.settings, parsed_args.verbosity)

    # if you want to modify the global namespace programmatically,
    # here is the right place to do so; this will extend / overwrite
    # the global variables specified on the command line
    additional_global_namespace = {}

    sw.process_templates(parsed_args.process_only_modified,
                         additional_global_namespace)
