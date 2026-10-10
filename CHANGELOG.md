## Unreleased — Python 3.14 migration (release decision pending)

- CPython >=3.12 metadata; qualified 3.12/3.13/3.14 standard with GIL on Linux x86_64 only.
- Build backend setuptools >=83.0.0 and test extra pytest >=9.0.3. Project/module names, nsURI, licenses and author credits are retained.
- Removed setuptools.command.test and legacy test hooks; retained CLI and EcoreGenerator API.
- Deterministic imports, package/output ordering and formatting; escaped strings, Unicode, keywords, defaults, subpackages and package dependencies are qualified.
- Templates ship in sdists/wheels; frozen old generated-code corpus remains separate from current candidate generation.

Keep old generated code until a reviewed comparison is available. Generate into a separate directory with pyecoregen -e model.ecore -o candidate; compile, import, instantiate and round-trip before replacing application sources.

# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project
adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## 0.5.1
### Fixed
- Multiple useless `EClass` and `EReference` imports.
- Opposite derived `EReference` name.


## 0.5.0
### Added

- Added generation of "many" derived `EStructuralFeature` as `EDerivedCollection`.
- Added support for non unique collections of `EAttribute`.

### Fixed
- Missing generation of "single" derived `EReference`.
- Keyword handling for metaclasses.

### Removed
- Removed support for Python 3.4.


## 0.4.3
### Added

- Added option to auto-generate the Python code for the metamodel's dependencies,
  see the `--with-dependencies` option.

### Fixed
- Missing imports to `EDataType` references that are contained in a metamodel dependency.
- Missing default value generation for `EAttribute`.
- Missing `eSubpackages` and `eSuperPackages` at module level.

### Removed
- Removed support for Python 3.3.

## 0.4.2
### Fixed

- Missing 'templates' in the sdist package. The sdist package (`.tar.gz`) is
  built using information of the `MANIFEST.in` for non-source files. The
  templates were simply missing in it.

## 0.4.1
### Fixed

- README

## 0.4.0
### Added

- Added option to auto-register generated package in global registry, see the
  `--auto-register-package` option.
- Added option to specify a user module, from where mixin classes. These mixins must then implement
  all end-user specific code like operations and derived attributes. See the `--user-module`
  command line option.

### Fixed

- EDatatype registration.
- Various derived attribute fixes.
