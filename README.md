# Poetry Hooks

![CI](https://github.com/jvrana/poetry-hooks/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/jvrana/poetry-hooks/branch/master/graph/badge.svg)](https://codecov.io/gh/jvrana/poetry-hooks)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/jvrana/poetry-hooks.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/jvrana/poetry-hooks/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/jvrana/poetry-hooks.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/jvrana/poetry-hooks/alerts/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

[Pre-commit](https://pre-commit.com/) hooks for [poetry](https://python-poetry.org/).

## Version up hook

Exports `pyproject.toml` project information to `<pkg>/_version.py`.
The `tool.poetry.packages` key is used. If multiple entries are found, the first
entry is used. Else, `tool.poetry.name` is used as the main package.

```yaml
-   repo: https://github.com/jvrana/poetry-hooks
    rev: 0.1.0
    hooks:
    -   id: poetry-version-up
```

You can change the default filename of the created version file by adding
the option to the pyproject.toml file (must end in .py):

```yaml
[tool.poetryhooks]
version_up_name = "_pkg_version.py"
```

## Export hook

Exports `pyproject.toml` to a `requirements.txt` file(s).
Multiple `requirement.txt` files are supported.

Basic usage:

```yaml
repos:
-   repo: https://github.com/jvrana/poetry-hooks
    rev: 0.1.0
    hooks:
    -   id: poetry-export
```

Exporting basic requirements + development requirements with custom filename.

```yaml
repos:
-   repo: https://github.com/jvrana/poetry-hooks
    rev: 0.1.0
    hooks:
    -   id: poetry-export
        args: ["--requirements", "requirements-dev.txt", "--poetry='--dev'"]
```

Exporting extra requirements:

```yaml
repos:
-   repo: https://github.com/jvrana/poetry-export-hook
    rev: 0.0.1a2
    hooks:
    -   id: poetry-export
        args: ["--requirements", "requirements-docs.txt", "--poetry='-E docs'"]
```


Verbose:

```yaml
repos:
-   repo: https://github.com/jvrana/poetry-hooks
    rev: 0.1.0
    hooks:
    -   id: poetry-export
        args: ["-vvv"]
```

Export basic, development, and doc requirement files:

```yaml
repos:
-   repo: https://github.com/jvrana/poetry-hooks
    rev: 0.1.0
    hooks:
    -   id: poetry-export
    -   id: poetry-export
        args: ['--requirements', 'requirements-dev.txt', "--poetry='--dev'"]    
    -   id: poetry-export
        args: ['--requirements', 'requirements-docs.txt', "--poetry='--dev -E docs'"]
```
