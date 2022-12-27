# StempelWerk

_Automatic code generation from Jinja2 templates_

<figure style="display: flex; flex-flow: column; max-width: 25em;">
  <img src="include/wallpaper-surface-printing-machine.jpg"
       alt="Illustration of an old printing machine" />
  <figurecaption>
    <small>
      <em>
        Illustration by Narcisse Navellier (obtained from
        <a href="https://commons.wikimedia.org/wiki/File:Wallpaper-surface-printing-machine.jpg">
          Wikimedia Commons</a>)
      </em>
    </small>
  </figurecaption>
</figure>

## Installation

StempelWerk was developed using Python v3.8, so an older version might
not work.

Run the following lines - possibly in a virtual environment - to
upgrade `pip` and install the dependencies:

```bash
python3 -m pip install --user --upgrade pip

# "namespace()" was introduced in v2.1.0
python3 -m pip install --user --upgrade "Jinja2>=2.1.0"
```

## Execution

Generate your code from templates by running the following command:

```bash
python3 ./src/StempelWerk.py [--only-modified] PATH_TO_SETTINGS_FILE
```

## Performance

By default, StempelWerk renders all template files located in the
specified template directory.

When you use the command line argument `--only-modified`, however,
StempelWerk tries to process only the template files that have changed
since the last successful run. Use of this command line argument is
highly discouraged in CI/CD pipelines!

_This logic is not infallible: some file systems update modification
times in a weird manner, and changes to master templates (called
"stencils" in StempelWerk) are currently not handled. However, in such
a case you can simply use StempelWerk without the `--only-modified`
argument._

## Settings

Settings for StempelWerk are provided in the form of a JSON file. The
path to this file is specified as command line argument.

_All paths should be specified relative to the path of
`StempelWerk.py`. For cross-platform compatibility, I recommend to use
a forward slash as path separator on all systems:
`/spam/eggs`. StempelWerk will handle all path separator conversions
for you._

### `template_dir`

Path to root of template directory. This directory is scanned
recursively and all files with an extension matching the setting
`included_file_extensions` will be rendered using Jinja2.

### `output_dir`

Path to root of output directory. Rendered files will be saved in this
directory.

### `stencil_dir_name`

Name of directory that contains stencils. All files in
`template_dir/stencil_dir_name` will be loaded into Jinja2 and can be
referenced from other templates at runtime.

In addition, files in any directory matching this name will not be
rendered.

### `included_file_extensions`

List containing file extensions (e.g. `*.sql.jinja`). Only files with
a [matching extension](https://docs.python.org/3/library/fnmatch.html)
are considered to be templates and will be passed to Jinja2.

### `update_environment`

List containing paths to Python files. After creating the Jinja2
environment, these files will be sorted alphabetically (to guarantee a
stable execution order) and executed. Use this feature to add filters
to the environment, or perform any other task Python is capable of.

_Warning: there are no security checks to prevent you from deleting
all of your files and doing other mischief, so please be careful!_

### `last_run_file`

Path to the file in which the time of the last successful run will be
stored.

**Default value: `../.last_run`**

_If your operating system handles temporary directories correctly
(Windows does not), you could store this file in one of them
(e.g. `/tmp/`). This way, all template files would be rendered once
after starting the system._

### `file_separator`

Each time this string is encountered in the rendered ouput of a
template, a new file is created. This allows you to create multiple
files from a single template.

**Default value: `### File: `**

_Please see example templates to learn how to use this feature._

## License

Copyright (c) 2020-2022 [Martin Zuther](https://www.mzuther.de/)

This program is free software and licensed under the terms of the [BSD
3-Clause License](./LICENSE.md). **Thank you for using free
software!**
