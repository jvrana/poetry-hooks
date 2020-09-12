
from poetry_hooks.utils import cmd_output
from poetry_hooks.export import main
from poetry_hooks.export import parse_args
from poetry_hooks.export import poetry_cmd
import pytest
from pathlib import Path
from contextlib import contextmanager
import toml


@pytest.fixture
def tempdir(tmpdir, pyproject):
    myproject = tmpdir.join('myproject').mkdir()
    with myproject.as_cwd():
        cmd_output('git', 'init')




class TestParseArgs:
    def test_parse_args_default(self):
        args = parse_args(argv=["f1", "f2"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 0
        assert args.dev is False
        assert args.extras == []

    def test_parse_args_requirements(self):
        args = parse_args(argv=["f1", "f2", "--requirements", "r.txt"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "r.txt"
        assert args.verbose == 0
        assert args.dev is False
        assert args.extras == []

    def test_parse_args_v(self):
        args = parse_args(argv=["f1", "f2", "-v"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 1
        assert args.dev is False
        assert args.extras == []

    def test_parse_args_vv(self):
        args = parse_args(argv=["f1", "f2", "-vv"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 2
        assert args.dev is False
        assert args.extras == []

    def test_parse_args_vvv(self):
        args = parse_args(argv=["f1", "f2", "-vvv"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 3
        assert args.dev is False
        assert args.extras == []

    def test_parse_args_dev(self):
        args = parse_args(argv=["f1", "f2", "-D"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 0
        assert args.dev is True
        assert args.extras == []

    def test_parse_args_extras1(self):
        args = parse_args(argv=["f1", "f2", "-E", "docs"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 0
        assert args.dev is False
        assert args.extras == ["docs"]

    def test_parse_args_extras2(self):
        args = parse_args(argv=["f1", "f2", "-E", "docs", "-E", "lint"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 0
        assert args.dev is False
        assert args.extras == ["docs", "lint"]


def test_poetry_cmd():
    out = poetry_cmd("requirements-dev.txt", True, ("docs", "linter"))
    expected = "poetry export -f requirements.txt --dev -E docs -E linter".split()
    o = " ".join(out)
    e = " ".join(expected)
    print(o)
    print(e)
    assert o == e


def test_adding_nothing(new_project):
    proj_ctx, _ = new_project
    with proj_ctx(git=True) as proj:
        proj.join('f.py').write('a'*1000)
        cmd_output('git', 'add', 'f.py')
        assert main(argv=["f.py"]) == 0


def test_adding_pyproject(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx(git=True):
        with pyproj_ctx():
            pass
        cmd_output("git", "add", "pyproject.toml")
        assert main(argv=["pyproject.toml"]) == 1


def test_adding_requirements(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx(git=True) as proj:
        with pyproj_ctx():
            pass
        f = "requirements.txt"
        proj.join(f).write("a" * 1000)
        cmd_output("git", "add", f)
        assert main(argv=[f]) == 1


def test_adding_lock(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx(git=True):
        with pyproj_ctx():
            pass
        f = "poetry.lock"
        assert main(argv=[f]) == 1


def test_adding_requirements_twice(new_project):
    proj_ctx, _ = new_project
    with proj_ctx(git=True) as proj:
        f = 'script.py'
        proj.join(f).write("a" * 1000)

        cmd_output("git", "add", f)
        assert main(argv=[f]) == 1

        cmd_output("git", "add", f)
        assert main(argv=[f]) == 0


def test_new_reqs_file_not_added(new_project):
    proj_ctx, _ = new_project
    with proj_ctx() as proj:
        # Should not fail since 'requirements-dev.txt' is not added to git yet
        f = "requirements.txt"
        proj.join(f).write("a" * 1000)
        cmd_output("git", "add", f)
        assert main(argv=[f, "--requirements", "requirements-dev.txt"]) == 0


def test_new_reqs_file_added(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx() as proj:
        with pyproj_ctx():
            pass
        # Should fail since 'requirements-dev.txt' is added to git
        f = "requirements-dev.txt"
        proj.join(f).write("a" * 1000)
        cmd_output("git", "add", f)
        assert main(argv=[f, "--requirements", f]) == 1
