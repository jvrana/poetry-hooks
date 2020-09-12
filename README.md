# Poetry Hooks

![Python package](https://github.com/jvrana/poetry-export-hook/workflows/Python%20package/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/jvrana/poetry-export-hook.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/jvrana/poetry-export-hook/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/jvrana/poetry-export-hook.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/jvrana/poetry-export-hook/alerts/)
[Pre-commit](https://pre-commit.com/) hook for exporting `requirements.txt` from `pyproject.toml` using [poetry](https://python-poetry.org/).

## Version up hook

This hook exports `pyproject.toml` project information to `<pkg>/__version__.py`

## Export hook

This hook exports `pyproject.toml` to a `requirements.txt` file(s).
Multiple `requirement.txt` files are supported.

Basic usage:

```yaml
repos:
-   repo: https://github.com/jvrana/poetry-export-hook
    rev: 0.0.1a2
    hooks:
    -   id: poetry-export
```

Exporting basic requirements + development requirements with custom filename.

```yaml
repos:
-   repo: https://github.com/jvrana/poetry-export-hook
    rev: 0.0.1a2
    hooks:
    -   id: poetry-export
        args: ["--requirements", "requirements-dev.txt", "--dev"]
```

Exporting extra requirements:

```yaml
repos:
-   repo: https://github.com/jvrana/poetry-export-hook
    rev: 0.0.1a2
    hooks:
    -   id: poetry-export
        args: ["--requirements", "requirements-docs.txt", "-E", "docs"]
```


Verbose:

```yaml
repos:
-   repo: https://github.com/jvrana/poetry-export-hook
    rev: 0.0.1a2
    hooks:
    -   id: poetry-export
        args: ["-vvv"]
```

Export basic, development, and doc requirement files:

```yaml
repos:
-   repo: https://github.com/jvrana/poetry-export-hook
    rev: 0.0.1a2
    hooks:
    -   id: poetry-export
    -   id: poetry-export
        args: ['--requirements', 'requirements-dev.txt', '--dev']    
    -   id: poetry-export
        args: ['--requirements', 'requirements-docs.txt', '--dev', '-E', 'docs']
```
