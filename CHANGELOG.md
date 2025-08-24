# Change Log

_All notable changes to this project will be documented in this
file. This change log follows the conventions of
[keepachangelog.com]._

_I tend to not use
[semantic versioning](https://semver.org/), but we will see what
happens._

<!--- ---------------------------------------------------------------------- -->

## [Unreleased]



<!--- ---------------------------------------------------------------------- -->

## [1.1.0] - 2025-08-24
### Added
- release StempelWerk as package on PyPI
- provide template filter `start_new_file`
- show loaded settings in verbose mode

### Changed
- use `uv` as package manager
- do not automatically create template and output directories
- load extensions and custom modules as early as possible
- load `herkules` module from package
- update libraries
- update tooling scripts
- rename example settings file
- move code to directory `src`

### Fixed
- fix: `root_dir` is not relative to current directory
- fix: JSON file with globals not loaded from path given as string

<!--- ---------------------------------------------------------------------- -->

## [1.0.6] - 2025-05-20

### Security
- update setuptools dependency to fix security vulnerability

<!--- ---------------------------------------------------------------------- -->

## [1.0.5] - 2025-03-11

### Security
- update Jinja2 dependency to fix security vulnerability

### Changed
- update copyrights

### Fixed
- fix: linter errors

<!--- ---------------------------------------------------------------------- -->

## [1.0.4] - 2024-12-26

### Security
- update Jinja2 dependency to fix security vulnerability

### Changed
- include files by matching glob, not only suffix
- factor out `DirWalk` into separate module and rename to `Hercules`
- add library to check licenses of dependencies

### Fixed
- fix: pass test script when no slow tests found
- fix: license is not recognized in poetry

<!--- ---------------------------------------------------------------------- -->

## [1.0.3] - 2024-07-17

### Security
- update setuptools dependency to fix security vulnerability

### Fixed
- fix: README contains vulnerable Jinja2 version

<!--- ---------------------------------------------------------------------- -->

## [1.0.2] - 2024-05-07

### Security
- update Jinja2 dependency (again) to fix security vulnerability

### Changed
- rename some `DirWalk` parameters
- add unit tests for `DirWalk` class
- run slow tests when all other tests have passed
- refactor code
- change directory layout of source code 

### Fixed
- fix: no files are included in case no suffixes are specified
- fix: excluded file names cannot use globs
- fix: poetry cannot find root folder

<!--- ---------------------------------------------------------------------- -->

## [1.0.1] - 2024-01-12

### Security
- update Jinja2 dependency to fix security vulnerability

### Changed
- move poetry calls to separate Bash script
- refactor code
- update dependencies
- update documentation

<!--- ---------------------------------------------------------------------- -->

## [1.0.0] - 2023-07-24

- This is the first stable release (although I have been using StempelWerk professionally for over a year now).

### Added
- use poetry to create virtual environment
- add common scripts for PowerShell

### Fixed
- fix: unit test erroneously finds stencil on Windows
  - Windows is not case-sensitive. It really should be, but it is not. Sigh.

<!--- ---------------------------------------------------------------------- -->

[keepachangelog.com]: http://keepachangelog.com/
[unreleased]: https://github.com/mzuther/StempelWerk/tree/develop
[1.0.0]: https://github.com/mzuther/StempelWerk/commits/v1.0.0
