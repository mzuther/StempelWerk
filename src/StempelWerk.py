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
    VERSION = '0.6.6'

    AUTHOR = 'Martin Zuther'
    LICENSE = 'BSD 3-Clause License'
    COPYRIGHT = f'{ APPLICATION } v{ VERSION }    (c) 2020-2023 { AUTHOR }'

    @staticmethod
    def display_version():
        print()
        print(f'[ { StempelWerk.COPYRIGHT } ]')
        print(f'[ Licensed under the { StempelWerk.LICENSE }           ]')
        print()

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
        jinja_options: list = dataclasses.field(
            default_factory=dict)
        jinja_extensions: list = dataclasses.field(
            default_factory=list)
        custom_modules: list = dataclasses.field(
            default_factory=list)
        last_run_file: str = '../.last_run'
        file_separator: str = '### File: '
        show_debug_messages: bool = False

        @staticmethod
        def finalize_path(root_dir, original_path):
            new_path = os.path.join(root_dir, original_path)
            new_path = os.path.expanduser(new_path)
            new_path = os.path.normpath(new_path)
            return new_path


        def __post_init__(self):
            # finalize paths
            self.template_dir = self.finalize_path(
                self.root_dir, self.template_dir)

            self.output_dir = self.finalize_path(
                self.root_dir, self.output_dir)

            self.last_run_file = self.finalize_path(
                self.root_dir, self.last_run_file)

    # ---------------------------------------------------------------------

    # Template class for customizing the Jinja environment
    class CustomCodeTemplate:  # noqa: E301
        def __init__(self, copy_of_settings):
            # this is only a copy; changing this variable does not change
            # the settings of StempelWerk
            self.settings = copy_of_settings

        def update_environment(self, jinja_environment):
            return jinja_environment

    # ---------------------------------------------------------------------

    def __init__(self, root_dir, config_file_path, show_debug_messages=False):
        self.display_version()
        self._load_settings(config_file_path, root_dir, show_debug_messages)


    def _print_error(self, message=''):
        if message:
            print(f'ERROR: { message }')
        else:
            print()


    def _print_debug(self, message=''):
        if not self.settings.show_debug_messages:
            return

        if message:
            print(f'DEBUG: { message }')
        else:
            print()


    def _load_settings(self, config_file_path, root_dir, show_debug_messages):
        root_dir = os.path.normpath(
            os.path.expanduser(root_dir))

        config_file_path = self.Settings.finalize_path(
            root_dir, config_file_path)

        try:
            config_load_error = False
            with open(config_file_path) as f:
                loaded_settings = json.load(f)
                loaded_settings['root_dir'] = root_dir
                loaded_settings['show_debug_messages'] = show_debug_messages

            # here's where the magic happens: unpack JSON file into class
            self.settings = self.Settings(**loaded_settings)

        except FileNotFoundError:
            self._print_error(f'File "{ config_file_path }" not found.')
            config_load_error = True

        except json.decoder.JSONDecodeError as err:
            self._print_error(f'File "{ config_file_path }" is broken:')
            self._print_error(f'{ err }')
            config_load_error = True

        except TypeError as err:
            self._print_error(f'Did you provide all settings in "{ config_file_path }"?')
            self._print_error(f'{ err }')
            self._print_error()

            # print traceback to help with debugging
            raise err

        if config_load_error:
            self._print_error()
            exit(1)


    def create_environment(self):
        # Jinja also loads templates from sub-directories
        template_loader = jinja2.FileSystemLoader(self.settings.template_dir)

        self.jinja_environment = jinja2.Environment(
            loader=template_loader, **self.settings.jinja_options)

        # list all templates in cache
        if self.settings.show_debug_messages:
            self._print_debug('Loaded templates:')
            self._print_debug(' ')

            for template_filename in self.jinja_environment.list_templates():
                self._print_debug(f'* { template_filename }')

            self._print_debug(' ')
            self._print_debug('Use relative paths to access templates in sub-directories')
            self._print_debug('(https://stackoverflow.com/a/9644828).')
            self._print_debug()

        # execute custom Python code
        self._update_environment()


    def _update_environment(self):
        # load Jinja extensions first so they can be referenced in custom
        # Python code
        for extension in self.settings.jinja_extensions:
            self._print_debug(f'Adding extension "{ extension }" ...')

            self.jinja_environment.add_extension(extension)

            self._print_debug('Done.')
            self._print_debug()

        # run custom Python code
        for module_name in self.settings.custom_modules:
            self._print_debug(f'Loading module "{ module_name }" ...')

            # import code as module
            module_spec = importlib.util.find_spec(
                module_name)
            imported_module = importlib.util.module_from_spec(
                module_spec)

            # execute module its own namespace
            module_spec.loader.exec_module(imported_module)
            custom_code = imported_module.CustomCode(
                copy.deepcopy(self.settings))

            self._print_debug('Updating environment ...')

            # finally, update the Jinja environment
            self.jinja_environment = custom_code.update_environment(
                self.jinja_environment)

            self._print_debug('Done.')
            self._print_debug()


    def render_template(self, template_filename):
        # create environment automatically
        if not hasattr(self, 'jinja_environment'):
            self.create_environment()

        template_filename = os.path.relpath(
            template_filename, self.settings.template_dir)
        print('[ {} ]'.format(template_filename))

        # render template
        try:
            # Jinja2 cannot handle Windows paths with backslashes
            template = self.jinja_environment.get_template(
                template_filename.replace(os.path.sep, '/'))
            content_of_multiple_files = template.render()

        except (jinja2.exceptions.TemplateSyntaxError,
                jinja2.exceptions.TemplateAssertionError) as err:
            self._print_error()
            self._print_error(f'{ err.message } (line { err.lineno })')
            self._print_error()

            raise(err)

        for content_of_single_file in content_of_multiple_files.split(
                self.settings.file_separator):
            # content starts with file_separator, so first string is empty
            # (or contains whitespace when a template is not well written)
            if not content_of_single_file.strip():
                continue

            # extract and normalize file name
            output_filename, content = content_of_single_file.split('\n', 1)

            output_filename = output_filename.strip()
            output_filename = os.path.join(
                self.settings.output_dir, output_filename)
            output_filename = os.path.abspath(output_filename)

            print('--> {}'.format(os.path.relpath(
                output_filename, self.settings.output_dir)))

            # ensure Batch files use Windows line endings, otherwise
            # seemingly random lines will be executed
            if output_filename.endswith('.bat'):
                newline = '\r\n'
            # in any other case, use default line ending of system
            else:
                newline = None

            # Jinja2 encodes all strings in UTF-8
            with open(output_filename, mode='w', encoding='utf-8',
                      newline=newline) as f:
                f.write(content)

            # make Linux shell files executable by owner
            if output_filename.endswith('.sh') and platform.system() == 'Linux':
                with pathlib.Path(output_filename) as f:
                    mode = f.stat().st_mode
                    f.chmod(mode | stat.S_IXUSR)

        print()


    def process_templates(self, process_only_modified=False):
        dirwalk_inclusions = {
            # do not render stencils
            'excluded_directory_names': [self.settings.stencil_dir_name],
            'excluded_file_names': [],
            'included_file_extensions': self.settings.included_file_extensions,
        }

        modified_after = None
        if process_only_modified:
            # get time of last run
            try:
                with open(self.settings.last_run_file) as f:
                    modified_after = f.read().strip()
            except IOError:
                modified_after = None

        # find all Jinja2 files in template directory
        template_filenames = dirwalk(
            self.settings.template_dir,
            included=dirwalk_inclusions,
            modified_after=modified_after)

        # only load Jinja2 when there are files that need to be processed
        if template_filenames:
            for template_filename in template_filenames:
                self.render_template(template_filename)

        # save time of current run
        with open(self.settings.last_run_file, mode='w') as f:
            current_timestamp = datetime.datetime.now().timestamp()

            # round down to ensure that files with inaccurate timestamps and
            # other edge cases are included
            current_timestamp = math.floor(current_timestamp)

            f.write(str(current_timestamp))


if __name__ == '__main__':
    # extremely primitive command line parsing
    class CommandLineArguments:
        def __init__(self):
            self.cla = copy.copy(sys.argv)
            del self.cla[0]

        def get_option(self, option):
            if option in self.cla:
                self.cla.remove(option)
                return True
            return False

        def get_config_path(self):
            if len(self.cla) != 1:
                self._print_error()
                self._print_error('Please provide JSON settings file as parameter.')
                self._print_error()
                exit(1)
                # highly sophisticated command line parsing
            return self.cla.pop()


    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ensure that this script can be called from anywhere
    os.chdir(script_dir)

    cla = CommandLineArguments()
    process_only_modified = cla.get_option('--only-modified')
    show_debug_messages = cla.get_option('--debug')
    config_file_path = cla.get_config_path()

    sw = StempelWerk(script_dir, config_file_path, show_debug_messages)
    sw.process_templates(process_only_modified)
