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

import json
import os
import pathlib
import platform
import stat
import sys

from dataclasses import dataclass

import jinja2
from DirWalk.DirWalk import dirwalk


VERSION = '0.3.1'

# ensure that this script can be called from anywhere
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Settings
# ========
#
# NOTE: all paths are relative to the path of this script; please
# NOTE  separate paths using forward slashes ("/a/b") for cross-platform
# NOTE  compatibility; StempelWerk will handle the conversion for you
#
# path to template directory; this directory is scanned recursively;
# all files with an extension of ".jinja" are rendered using Jinja2
#
# name of directory that contains main templates ("stencils"); files
# in directories matching this name will be ignored and not rendered
#
# each time this string is encountered, a new file is created; this
# allows you to create multiple files from a single template
#
# path to output root directory for rendered files


# Auto-create classes to write leaner code
#
# The "@dataclass" decorator creates a class, class members, and a
# constructor with key-word parameters that have default values.
#
# In addition, this allows us to address settings with the more
# readable membership operator ("settings.template_dir") instead
# of using dictionary access ("settings['template_dir']").
@dataclass
class Settings:
    template_dir: str
    output_dir: str
    stencil_dir_name: str
    included_file_extensions: list
    file_separator: str = '### File: '

    def __post_init__(self):
        # finalize paths
        self.template_dir = os.path.normpath(
            os.path.join(script_dir, self.template_dir))

        self.output_dir = os.path.normpath(
            os.path.join(script_dir, self.output_dir))


def load_settings(config_file_path):
    config_file_path = os.path.normpath(
        os.path.expanduser(config_file_path))

    try:
        config_load_error = False
        with open(config_file_path) as f:
            loaded_settings = json.load(f)

        # here's where the magic happens: unpack JSON file into classes
        settings = Settings(**loaded_settings)

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

        # print traceback
        raise err

    if config_load_error:
        print()
        exit(1)

    return settings


# NOTE: use relative paths to access templates in sub-directories
# (https://stackoverflow.com/a/9644828)
def cache_templates(settings, list_templates=False):
    # directories containing templates (no need to add sub-directories)
    template_dir = [settings.template_dir]
    templateLoader = jinja2.FileSystemLoader(template_dir)
    cached_templates = jinja2.Environment(
        loader=templateLoader, trim_blocks=True)

    # list all templates in cache
    if list_templates:
        print('Templates:')
        for template_filename in cached_templates.list_templates():
            print('* {}'.format(template_filename))
        print()

    return cached_templates


def render_template(settings, cached_templates, template_filename):
    template_filename = os.path.relpath(
        template_filename, settings.template_dir)
    print('[ {} ]'.format(template_filename))

    # render template
    template = cached_templates.get_template(
        # Jinja2 cannot handle Windows paths with backslashes
        template_filename.replace(os.path.sep, '/'))
    content_of_multiple_files = template.render()

    for content_of_single_file in content_of_multiple_files.split(
            settings.file_separator):
        # content starts with file_separator, so first string is empty
        # (or contains whitespace when a template is not well written)
        if not content_of_single_file.strip():
            continue

        # extract and normalize file name
        output_filename, content = content_of_single_file.split('\n', 1)
        output_filename = os.path.abspath(
            os.path.join(settings.output_dir, output_filename.strip()))

        print('--> {}'.format(os.path.relpath(
            output_filename, settings.output_dir)))

        # ensure Batch files use Windows line endings, otherwise
        # seemingly random lines will be executed
        if output_filename.endswith('.bat'):
            newline = '\r\n'
        # in any other case, use default line ending of system
        else:
            newline = None

        # Jinja2 encodes all strings in UTF-8
        with open(
                output_filename, mode='w', encoding='utf-8',
                newline=newline) as f:
            f.write(content)

        # make Linux shell files executable by owner
        if output_filename.endswith('.sh') and platform.system() == 'Linux':
            with pathlib.Path(output_filename) as f:
                mode = f.stat().st_mode
                f.chmod(mode | stat.S_IXUSR)

    print()


def process_templates(settings_path):
    settings = load_settings(settings_path)

    # do not end entries with path separators ("/" or "\")!
    inclusions = {
        'excluded_directory_names': [
            # do not render main templates ("stencils")
            settings.stencil_dir_name,
        ],
        'excluded_file_names': [],
        'included_file_extensions': settings.included_file_extensions,
    }

    # load and cache main templates ("stencils")
    cached_templates = cache_templates(settings, list_templates=False)

    # find all Jinja2 files in template directory
    for template_filename in dirwalk(
            settings.template_dir,
            included=inclusions,
            modified_after=None):
        render_template(settings, cached_templates, template_filename)


def display_version():
    print()
    print(f'[ StempelWerk v{ VERSION }    (c) 2020-2022 Martin Zuther ]')
    print('[ Licensed under the BSD 3-Clause License           ]')
    print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print()
        print('ERROR: Please provide JSON settings file as first parameter.')
        print()

        exit(1)

    display_version()

    # settings path is relative to the path of this script
    settings_path = os.path.join(script_dir, sys.argv[1])

    process_templates(settings_path)
