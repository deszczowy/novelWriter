# Contributing Guide

When contributing to this repository, please first discuss the change you wish to make with the
owner. Either via the issue tracker or on the discussions page. Especially if it is regarding new
features. If you just want to make a minor correction, like fix a typo or similar, feel free to
just make a pull request directly.

**The following contributions are welcome:**

* Bugfixes for new or existing bugs. Please also report new bugs in the issue tracker even if you
  also provide a fix. It makes it easier to keep track of what has been fixed and when.
* Translations made via the [Crowdin project page](https://crowdin.com/project/novelwriter).
* Improvements to the documentation. Particularly if the documentation is unclear. Please don't
  make any larger changes to the documentation without discussing them with the maintainer first.
* Adaptations, installation or packaging features targeting specific operating systems.

**Please do not:**

* Make a pull request that restructures or reformats existing code. If you think some part of the
  code could be improved, please make an issue thread or start a discussion. The same applies to
  any text document in the repository.

## Picking the Correct Branch for a Pull Request

The `main` branch is the default branch. For general changes, please make a new branch in your own
fork from the current `main` branch. Do not make pull requests from your copy of the `main` branch.

As of April 2024, releases are made from the `release` branch. If you are submitting a fix to a
current release you must do so from the `release` branch. If you make such a fix on the `main`
branch, **it cannot be included in a patch release**. This also applies to the documentation for
the latest release published on the main website.

**Also check the following:**

* Make sure your code passes all tests and conforms to the style guide. You can check that the
  code generally conforms by running the Python linting tool `flake8` from the root of the project
  folder, although it doesn't check everything. The same check is also run on pull requests.
* Please provide a description of the changes in the pull request under the summary section of the
  pull request template, and reference any related issues by providing the issue number.
* Do not change the version number.
* Do not submit files that were not actively changed but have otherwise been modified. This is
  mostly an issue with translation files. The language tool may update all files in the `i18n`
  folder.

## Code of Conduct

There is a code of conduct. Please follow it in all your interactions with the project.

### Our Pledge

In the interest of fostering an open and welcoming environment, we as contributors and maintainers
pledge to making participation in our project and our community a harassment-free experience for
everyone, regardless of age, body size, disability, ethnicity, gender identity and expression,
level of experience, nationality, personal appearance, race, religion, or sexual identity and
orientation.

Please see the [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md) file for the full text.

## Code Style Guide

The source code of novelWriter broadly follows the [PEP8](https://www.python.org/dev/peps/pep-0008)
style guide, but with a few exceptions. Some key points are listed below.

**Line Length:**

* Source code lines can extend to the upper limit of 99 characters allowed by PEP8. 79 characters
  is the recommended line length in PEP8, but this is often too restrictive. 99 characters are
  acceptable when that is more practical. Readability has priority. Generally, if a code statement
  requires multiple lines, the lines should wrap at 79 characters if possible. If wrapping can be
  avoided by going to 99, then that is generally preferable.
* For text files, the text should be wrapped at 99 character. The exception is markdown image tags
  and urls which can run past that limit.

**Variable and Function Names**

* PEP8 allows for camelCase for consistency with existing code. The Qt library uses camelCase, so
  the novelWriter source code does too.
* The exception to the above is for constants. They should always be in upper snake case, like PEP8
  states.

**Spaces, Indentation and Alignment**

* Only indentation by multiples of 4 spaces is allowed.
* No trailing spaces should occur on any line in the source code, including empty lines.
* All common line wrapping methods are allowed in the code, but avoid deep indentations.
* Aligning operators and attributes in columns with multiple spaces is not allowed by PEP8. The
  rule is relaxed a bit here. Alignment is allowed when populating large dictionaries or setting
  many class attributes. It does improve readability in such cases, but should not be overused.

**Type Annotation**

* All functions must be properly type annotated, and a return type stated in all cases.
* Do not use `List`, `Dict`, `Tuple`, etc, annotations that were deprecated in Python 3.9. You can
  install the `flake8-pep585` extension to make sure you don't forget. This is also checked by the
  syntax action run on pull requests.
* If annotations require a more recent Python version than the minimum version stated in the
  project's `pyproject.toml`, hide it under an `if TYPE_CHECKING` condition so that the code can
  still run on older versions. It's OK to require a more recent version for development.

### Linting with `flake8`

A good tool for checking Python code for errors and code style is `flake8`. The documentation is
available [here](https://flake8.pycqa.org/en/latest/).

The `.flake8` file in the root of this project has the following settings for that matches the
required code style:

```conf
[flake8]
ignore = E133,E221,E226,E228,E241,W503
max-line-length = 99
exclude = docs/*
```

The command line equivalent, with reporting, is:
```bash
flake8 . --count --ignore E133,E221,E226,E228,E241,W503 --max-line-length=99 --show-source --statistics
```

Passing this check is required before contributions are merged. This is checked automatically when
you make a pull request. You can run the `flake8` command locally to check beforehand. The full
command will give you a detailed description of the code lines that do not conform to the standard.

Two of the ignored errors are due to the relaxed restriction on column alignment, these are the
E221 and E241 error codes.

The code E226 is ignored because it doesn't actually follow the
[PEP8 recommendation](https://www.python.org/dev/peps/pep-0008/#other-recommendations)
of grouping longer equations by operator precedence like `2*a + 3*b` instead of `a * a + 3 * b`.
Generally, don't use spaces around `*`, `/` and `**`, but _do_ use spaces around `+` and `-`.
The same applies to the modulo operator `%`, hence E228 is also ignored.
