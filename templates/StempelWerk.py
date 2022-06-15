#! /usr/bin/python3

# ----------------------------------------------------------------------------
#
#  StempelWerk 0.1
#  ===============
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

import os
import pathlib
import platform
import stat
import sys

import jinja2

# ensure that this script can be called from anywhere
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Settings
# ========
#
# template directory that is scanned recursively (must be *relative*
# to script directory); all files with an extension of ".jinja" are
# rendered using Jinja2
template_dir = '.'

# directory with common template settings; files in this directory
# are ignored and not rendered
settings_dir = '_templates'

# each time this string is encountered, a new file is created; this
# allows you to create multiple files from a single template
file_separator = '### File: '

# output root directory for rendered files; joining paths one by one
# adds the correct path separator for the current operating system
output_dir = os.path.join(script_dir, '..', 'output')


# note: use relative paths to access templates in sub-directories
# (https://stackoverflow.com/a/9644828)
def cache_templates(template_dir, list_templates=False):
    # directories containing templates (no need to add sub-directories)
    template_dir = [template_dir]
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


def render_template(cached_templates, template_filename, output_dir):
    template_filename = os.path.relpath(template_filename, template_dir)
    template_filename = template_filename.replace(os.path.sep, '/')
    print('[ {} ]'.format(template_filename))

    # render template
    template = cached_templates.get_template(template_filename)
    content_of_multiple_files = template.render()

    for content_of_single_file in content_of_multiple_files.split(
            file_separator):
        # content starts with file_separator, so first string is empty
        # (or contains whitespace when a template is not well written)
        if not content_of_single_file.strip():
            continue

        # extract and normalize file name
        output_filename, content = content_of_single_file.split('\n', 1)
        output_filename = os.path.abspath(
            os.path.join(output_dir, output_filename.strip()))

        print('--> {}'.format(os.path.relpath(output_filename, output_dir)))

        # ensure Batch files use Windows line endings, otherwise
        # seemingly random lines will be executed
        if output_filename.endswith('.bat'):
            newline = '\r\n'
        # otherwise, use default line ending of system
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


if __name__ == '__main__':
    print()
    print('Python: {}'.format(sys.version))
    print('Jinja2: {}'.format(jinja2.__version__))
    print()

    cached_templates = cache_templates(template_dir, list_templates=False)
    template_filenames = []

    # find all Jinja2 files in template directory
    for root_dir, _, files in os.walk(template_dir):
        # do not render settings
        if root_dir.startswith(os.path.join(template_dir, settings_dir)):
            continue

        for filename in files:
            if filename.endswith('.jinja'):
                template_filenames.append([root_dir, filename])

    # sort templates by location and render each one
    for root_dir, filename in sorted(template_filenames):
        template_filename = os.path.join(root_dir, filename)
        render_template(cached_templates, template_filename, output_dir)
