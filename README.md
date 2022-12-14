# StempelWerk

_Automatic code generation from Jinja2 templates_

Generate your code by running the following command:

```bash
python3 ./src/StempelWerk.py PATH_TO_SETTINGS_FILE
```

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

Name of directory that contains master templates (called "stencils" in
StempelWerk). All files in `template_dir/stencil_dir_name` will be
loaded into Jinja2 and can be referenced from other templates at
runtime.

In addition, files in any directory matching this name will not be
rendered.

### `included_file_extensions`

List containing file extensions (e.g. `.sql`). Only files with a
matching extension are considered to be templates and will be passed
to Jinja2.

### `file_separator`

Each time this string is encountered in the rendered ouput of a
template, a new file is created. This allows you to create multiple
files from a single template.

_Please see example templates to learn how to use this feature._

## License

Copyright (c) 2020-2022 [Martin Zuther](https://www.mzuther.de/)

This program is free software and licensed under the terms of the [BSD
3-Clause License](./LICENSE.md). **Thank you for using free
software!**
