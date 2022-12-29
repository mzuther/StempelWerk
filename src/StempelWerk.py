#! /usr/bin/python3

# ----------------------------------------------------------------------------
#
#  StempelWerk
#  ===========
#  Automatic code generation from Jinja2 templates
#
#  Copyright (c) 2020-2022 Martin Zuther (https://www.mzuther.de/)
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

import dataclasses
import datetime
import json
import math
import os
import pathlib
import platform
import stat
import sys

import jinja2
from DirWalk.DirWalk import dirwalk


class StempelWerk:
    VERSION = '0.6.2'

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
        jinja_extensions: list = dataclasses.field(
            default_factory=list)
        execute_python_scripts: list = dataclasses.field(
            default_factory=list)
        last_run_file: str = '../.last_run'
        file_separator: str = '### File: '

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


    def __init__(self, root_dir, config_file_path, show_debug_messages=False):
        self._display_version()

        self.show_debug_messages = show_debug_messages
        self.root_dir = os.path.normpath(os.path.expanduser(root_dir))

        self._load_settings(config_file_path)


    def _display_version(self):
        print()
        print(f'[ StempelWerk v{ self.VERSION }    (c) 2020-2022 Martin Zuther ]')
        print('[ Licensed under the BSD 3-Clause License           ]')
        print()


    def _load_settings(self, config_file_path):
        config_file_path = self.Settings.finalize_path(
            self.root_dir, config_file_path)

        try:
            config_load_error = False
            with open(config_file_path) as f:
                loaded_settings = json.load(f)
                loaded_settings['root_dir'] = self.root_dir

            # here's where the magic happens: unpack JSON file into class
            self.settings = self.Settings(**loaded_settings)

        except FileNotFoundError:
            print(f'ERROR: File "{ config_file_path }" not found.')
            config_load_error = True

        except json.decoder.JSONDecodeError as err:
            print(f'ERROR: File "{ config_file_path }" is broken:')
            print(f'ERROR: { err }')
            config_load_error = True

        except TypeError as err:
            print(f'ERROR: Did you provide all settings in "{ config_file_path }"?')
            print(f'ERROR: { err }')
            print()

            # print traceback to help with debugging
            raise err

        if config_load_error:
            print()
            exit(1)


    def _create_environment(self):
        # NOTE: use relative paths to access templates in sub-directories
        # (https://stackoverflow.com/a/9644828)
        #
        # directories containing templates (no need to add sub-directories)
        template_dir = [self.settings.template_dir]
        templateLoader = jinja2.FileSystemLoader(template_dir)
        self.jinja_environment = jinja2.Environment(
            loader=templateLoader, trim_blocks=True)

        # list all templates in cache
        if self.show_debug_messages:
            print('DEBUG: Templates:')
            for template_filename in self.jinja_environment.list_templates():
                print('DEBUG: * {}'.format(template_filename))
            print()

        # execute custom Python code
        self._update_environment()


    def _update_environment(self):
        # load Jinja extensions first so they can be referenced in custom
        # Python code
        for extension in self.settings.jinja_extensions:
            if self.show_debug_messages:
                print(f'DEBUG: Adding extension "{ extension }" ...')

            self.jinja_environment.add_extension(extension)

            if self.show_debug_messages:
                print(f'DEBUG: Done.')
                print()

        # run custom Python code; sort filenames to guarantee a stable
        # execution order
        for code_filename in sorted(self.settings.execute_python_scripts):
            if self.show_debug_messages:
                print(f'DEBUG: Executing "{ code_filename}" ...')

            try:
                with open(code_filename) as f:
                    custom_code = f.read()

            except FileNotFoundError:
                print(f'ERROR: File "{ code_filename }" not found.')
                print()
                exit(1)

            # FIXME: don't do this at home -- I'm a professional :)
            jinja_environment = self.jinja_environment
            show_debug_messages = self.show_debug_messages

            compiled_code = compile(custom_code, code_filename, mode='exec')
            exec(compiled_code)

            # FIXME: don't do this at home -- really, don't!!!
            self.jinja_environment = jinja_environment

            if self.show_debug_messages:
                print(f'DEBUG: Done.')
                print()


    def render_template(self, template_filename):
        template_filename = os.path.relpath(
            template_filename, self.settings.template_dir)
        print('[ {} ]'.format(template_filename))

        # render template
        try:
            template = self.jinja_environment.get_template(
                # Jinja2 cannot handle Windows paths with backslashes
                template_filename.replace(os.path.sep, '/'))
            content_of_multiple_files = template.render()
        except (jinja2.exceptions.TemplateSyntaxError,
                jinja2.exceptions.TemplateAssertionError) as err:
            print()
            print(f'ERROR: { err.message } (line { err.lineno })')
            print()

            raise(err)

        for content_of_single_file in content_of_multiple_files.split(
                self.settings.file_separator):
            # content starts with file_separator, so first string is empty
            # (or contains whitespace when a template is not well written)
            if not content_of_single_file.strip():
                continue

            # extract and normalize file name
            output_filename, content = content_of_single_file.split('\n', 1)
            output_filename = os.path.abspath(
                os.path.join(self.settings.output_dir, output_filename.strip()))

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
            'excluded_directory_names': [
                # do not render stencils
                self.settings.stencil_dir_name,
            ],
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
            # create Jinja2 environment and pre-load stencils
            self._create_environment()

            # process templates
            for template_filename in template_filenames:
                self.render_template(template_filename)

        # save time of current run
        with open(self.settings.last_run_file, mode='w') as f:
            # round down to ensure that files with inaccurate timestamps and
            # other edge cases are included
            current_timestamp = math.floor(
                datetime.datetime.now().timestamp())

            f.write(str(current_timestamp))


if __name__ == '__main__':
    show_debug_messages = False

    if len(sys.argv) < 2:
        print()
        print('ERROR: Please provide JSON settings file as first parameter.')
        print()

        exit(1)

    command_line_arguments = list(sys.argv)
    process_only_modified = False

    # extremely primitive command line parsing
    if '--only-modified' in command_line_arguments:
        process_only_modified = True
        command_line_arguments.remove('--only-modified')

    # ensure that this script can be called from anywhere
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)

    # highly sophisticated command line parsing
    config_file_path = command_line_arguments.pop()

    sw = StempelWerk(root_dir, config_file_path, show_debug_messages)
    sw.process_templates(process_only_modified)
