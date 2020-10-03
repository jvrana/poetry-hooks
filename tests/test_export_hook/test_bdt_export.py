import inspect

import pytest
import toml
from poetry_hooks.export import main
from poetry_hooks.utils import DottedDict


class TestBehaviorDrivenTests:
    @pytest.mark.parametrize(
        "params",
        [
            pytest.param(
                {
                    "git": True,
                    "pkg": "mypkg",
                    "pyproject": True,
                    "results": [
                        {
                            "raises": None,
                            "paths": {
                                "requirements.txt": lambda x: not x.isfile(),
                                "poetry.lock": lambda x: not x.isfile(),
                                "pyproject.toml": lambda x: x.isfile(),
                                "mypkg": lambda x: x.isdir(),
                            },
                            "exit_code": 1,
                        },
                        {
                            "raises": None,
                            "paths": {
                                "requirements.txt": lambda x: x.isfile(),
                                "poetry.lock": lambda x: x.isfile(),
                                "pyproject.toml": lambda x: x.isfile(),
                                "mypkg": lambda x: x.isdir(),
                            },
                            "exit_code": 0,
                        },
                    ],
                },
                id="all files missing, creates files",
            ),
            pytest.param(
                {
                    "git": True,
                    "pkg": False,
                    "pyproject": True,
                    "results": [
                        {
                            "raises": None,
                            "paths": {
                                "requirements.txt": lambda x: not x.isfile(),
                                "poetry.lock": lambda x: not x.isfile(),
                                "pyproject.toml": lambda x: x.isfile(),
                                "mypkg": lambda x: not x.isdir(),
                            },
                            "exit_code": 1,
                        },
                        {
                            "raises": None,
                            "paths": {
                                "requirements.txt": lambda x: x.isfile(),
                                "poetry.lock": lambda x: x.isfile(),
                                "pyproject.toml": lambda x: x.isfile(),
                                "mypkg": lambda x: not x.isdir(),
                            },
                            "exit_code": 0,
                        },
                    ],
                },
                id="main pkg missing, not needed",
            ),
            pytest.param(
                {
                    "git": True,
                    "pkg": None,
                    "pyproject": False,
                    "results": [
                        {
                            "raises": RuntimeError,
                            "paths": {
                                "requirements.txt": lambda x: not x.isfile(),
                                "poetry.lock": lambda x: not x.isfile(),
                                "pyproject.toml": lambda x: not x.isfile(),
                            },
                        }
                    ],
                },
                id="pyproject.toml missing raises FileNotFoundError",
            ),
            pytest.param(
                {
                    "git": True,
                    "pkg": "mypkg",
                    "pyproject": True,
                    "results": [
                        {
                            "args": [
                                "--requirements",
                                "requirements-dev.txt",
                                "--poetry='--dev'",
                            ],
                            "paths": {
                                "requirements.txt": lambda x: not x.isfile(),
                                "requirements-dev.txt": lambda x: not x.isfile(),
                                "poetry.lock": lambda x: not x.isfile(),
                            },
                            "exit_code": 1,
                        },
                        {
                            "args": [
                                "--requirements",
                                "requirements-dev.txt",
                                "--poetry='--dev'",
                            ],
                            "paths": {
                                "requirements.txt": lambda x: not x.isfile(),
                                "requirements-dev.txt": lambda x: x.isfile(),
                                "poetry.lock": lambda x: x.isfile(),
                            },
                            "exit_code": 0,
                        },
                    ],
                },
                id="create requirements-dev.txt",
            ),
            pytest.param(
                {
                    "git": True,
                    "pkg": "mypkg",
                    "pyproject": True,
                    "results": [
                        {
                            "args": [
                                "--requirements",
                                "requirements-extras.txt",
                                "--poetry='-E myextras'",
                            ],
                            "paths": {
                                "requirements.txt": lambda x: not x.isfile(),
                                "requirements-extras.txt": lambda x: not x.isfile(),
                                "poetry.lock": lambda x: not x.isfile(),
                            },
                            "exit_code": 1,
                        },
                        {
                            "args": [
                                "--requirements",
                                "requirements-extras.txt",
                                "--poetry='-E myextras'",
                            ],
                            "paths": {
                                "requirements.txt": lambda x: not x.isfile(),
                                "requirements-extras.txt": lambda x: x.isfile(),
                                "poetry.lock": lambda x: x.isfile(),
                            },
                            "exit_code": 0,
                        },
                    ],
                },
                id="create with extras",
            ),
            pytest.param(
                {
                    "git": True,
                    "pyproject": "mypkg",
                    "pyproject": {"tool.poetry.version": "1.0.1"},
                    "results": [
                        {
                            "paths": {
                                "pyproject.toml": lambda x: toml.loads(x.read())[
                                    "tool"
                                ]["poetry"]["version"]
                                == "1.0.1"
                            },
                            "exit_code": 1,
                        },
                        {
                            "exit_code": 0,
                        },
                    ],
                }
            ),
        ],
    )
    def test_cases(self, new_project, params):
        proj_ctx, pyproj_ctx = new_project

        git = params.get("git", True)
        pkg = params.get("pkg", "mypkg")
        pyproj_data = params.get("pyproject", True)
        with proj_ctx(git=git, pkg=pkg) as proj:
            if pyproj_data:
                with pyproj_ctx() as pyproj:
                    pyproj = DottedDict(pyproj)
                    print(pyproj)
                    if isinstance(pyproj_data, dict):
                        for k, v in pyproj_data.items():
                            pyproj.set(k, v)
            for ith_result, result in enumerate(params.get("results", [])):
                for f, func in result.get("paths", {}).items():
                    path = proj.join(f)
                    passes = func(path)
                    if not passes:
                        msg = (
                            "Result ({}) did not pass the following"
                            "\nFailing condition: {}".format(
                                ith_result, inspect.getsource(func).strip()
                            )
                        )
                        raise AssertionError(msg)
                args = result.get("args", tuple())
                if result.get("raises"):
                    with pytest.raises(result["raises"]):
                        exit_code = main(args)
                else:
                    exit_code = main(args)
                if result.get("exit_code", None) is not None:
                    assert exit_code == result["exit_code"]
