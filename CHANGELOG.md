# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Corrected handling of Equation of Time in orbit (off by default)
- Made ASSERT in ExtData more explicit in case of missing variables.

### Fixed

- Corrected Python code generator scripts for component import/export specs.
- Add directories to `.gitignore` for building with `mepo`
- Bug building with mixed Intel/GCC compilers
- Set correct ESMA_env tag in `components.yaml`

### Removed

- Removed support for `checkout_externals` and moved solely to `mepo`
  - Removed `Externals.cfg`
  - Removed `checkout_externals` code in `CMakeLists.txt`

### Added

- Added configuration for CircleCI
  - Builds MAPL using GCC 9.2.0 and Open MPI 4.0.2
  - Builds and runs `pFIO_tests` and `MAPL_Base_tests`
- Imported Python/MAPL subdir (old, but never imported to GitHub)

	
## [2.0.2] - 2020-03-10

### Fixed

- Fix for handling coarse grids at high-resolution in ExtData

## [2.0.1] - 2019-03-02

### Fixed

- Restoring functionality with the tripolar grid that was lost when the develop branch was merged into master for version 2.0.0

## [2.0.0] - 2019-02-07

### Added

- New IO server implemented in PFIO library.
- New command line arguments to the MAPL_Cap to run multiple input and output servers on dedicated resources.

### Changed

- Code that uses MAPL should now `use MAPL` instead of `use MAPL_Mod`.
- CMakeLists.txt using MAPL should now have dependencies to `MAPL` and not `MAPL_Base`.
- History and ExtData component use the PFIO IO server for all file access. Default mode is to run the IO servers on the same resources as the application.
- The ExtData and History components use ESMF regridding for all operations and replace the FV3 regridding routines used for bilinear regridding and the MAPL tiling regridder for conservative regridding.

## [1.1.13] - 2019-12-09

### Fixed

- Correct handling of vector regridding in MAPL_CFIO.F90 layer

## [1.1.12] - 2019-12-03

### Added

- Added `CHANGELOG.md`

### Fixed

- Check status of round robin and make sure that the nodearray is allocated
- Allow per-cell counters to be properly reset (if they are needed)
- Must create file unit on all processors (`all_pes=.true.`) when writing binary History output

## [1.1.11] - 2019-09-24

### Added

- Added the option to add a prefix to the name in `GetFriendlies`

## [1.1.10] - 2019-09-18

### Fixed

- Fix a bug with exact reply using binary files

## [1.1.9] - 2019-09-18

### Changed

- Make `MAPL_ESMFStateReadFromFile` routine public

## [1.1.8] - 2019-09-18

### Added

- Add ability to change step size for average sun angle for LDAS

## [1.1.7] - 2019-08-15

### Fixed

- Fixes for the EASE index

### Added

- Add support for LDAS ensembles

## [1.1.6] - 2019-08-01

### Fixed

- Updates to allow MAPL to better support the tripolar grid

## [1.1.5] - 2019-07-26

### Fixed

- Fixes made to `MAPL_TilingRegridder.F90`

## [1.1.4] - 2019-07-26

### Fixed

- Changes to correct for new pressure after horizontal regridding

## [1.1.3] - 2019-07-25

### Changed

- Moved to use ESMA_cmake v1.0.9
- Use the new `LATEX_FOUND` capability of `ESMA_cmake` to determine if TeX processing can occur

## [1.1.2] - 2019-07-24

### Added

- Added `CODEOWNERS` file

### Removed

- Deleted unneeded GNUmakefiles

## [1.1.1] - 2019-07-08

### Changed

- Install Perl script missed in last release

## [1.1.0] - 2019-07-03

### Added

- First commit of MAPL 1.x with semantic versioning on GitHub