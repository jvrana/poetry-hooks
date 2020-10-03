import pytest
from poetry_hooks.export import logger
from poetry_hooks.export import main
from poetry_hooks.export import parse_args
from poetry_hooks.export import poetry_cmd
from poetry_hooks.utils import cmd_output


@pytest.fixture
def tempdir(tmpdir, pyproject):
    myproject = tmpdir.join("myproject").mkdir()
    with myproject.as_cwd():
        cmd_output("git", "init")


class TestParseArgs:
    def test_parse_args_default(self):
        args = parse_args(argv=["f1", "f2"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 0

    def test_parse_args_default_2(self):
        namespace = parse_args(argv=["f1", "f2", "--poetry='--otherarg -E docs'"])
        assert namespace.filenames == ["f1", "f2"]
        assert namespace.requirements == "requirements.txt"
        assert namespace.verbose == 0
        assert namespace.poetry == ['--otherarg', '-E', 'docs']

    def test_parse_args_requirements(self):
        args = parse_args(
            argv=["f1", "f2", "--requirements", "r.txt", "--poetry='--without-hashes'"]
        )
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "r.txt"
        assert args.verbose == 0
        assert args.poetry == ["--without-hashes"]

    def test_parse_args_v(self):
        args = parse_args(argv=["f1", "f2", "-v"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 1

    def test_parse_args_vv(self):
        args = parse_args(argv=["f1", "f2", "-vv"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 2

    def test_parse_args_vvv(self):
        args = parse_args(argv=["f1", "f2", "-vvv"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 3

    def test_parse_args_dev(self):
        args = parse_args(argv=["f1", "f2", "--poetry='-D'"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 0

    def test_parse_args_extras1(self):
        args = parse_args(argv=["f1", "f2", "--poetry='-E docs'"])
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 0
        assert args.poetry == ['-E', 'docs']

    def test_parse_args_extras2(self):
        args = parse_args(
            argv=["f1", "f2", "--poetry='-E docs -E lint'"]
        )
        assert args.filenames == ["f1", "f2"]
        assert args.requirements == "requirements.txt"
        assert args.verbose == 0
        assert args.poetry == ["-E", "docs", "-E", "lint"]


def test_poetry_cmd():
    out = poetry_cmd("--dev", "-E", "docs")
    expected = "poetry export -f requirements.txt --dev -E docs".split()
    o = " ".join(out)
    e = " ".join(expected)
    assert o == e


def test_argv_none(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx(git=True) as proj:
        with pyproj_ctx():
            pass
        proj.join("requirements.txt").write("")
        proj.join("f.py").write("a" * 1000)
        cmd_output("git", "add", "f.py")
        assert main(argv=None) == 0


def test_adding_nothing(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx(git=True) as proj:
        with pyproj_ctx():
            pass
        proj.join("requirements.txt").write("")
        proj.join("f.py").write("a" * 1000)
        cmd_output("git", "add", "f.py")
        assert main(argv=["f.py"]) == 0
        assert proj.join("requirements.txt").isfile()


def test_missing_requirments(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx(git=True) as proj:
        with pyproj_ctx():
            pass
        proj.join("f.py").write("a" * 1000)
        cmd_output("git", "add", "f.py")
        assert main(argv=["f.py"]) == 1
        assert proj.join("requirements.txt").isfile()


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
    with proj_ctx(git=True) as proj:
        with pyproj_ctx():
            pass
        f = "poetry.lock"
        assert not proj.join("poetry.lock").isfile()
        assert not proj.join("requirements.txt").isfile()
        assert main(argv=[f]) == 1
        assert proj.join("poetry.lock").isfile()
        assert proj.join("requirements.txt").isfile()


def test_adding_requirements_twice(new_project):
    logger.setLevel("DEBUG")
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx(git=True) as proj:
        with pyproj_ctx():
            pass
        f = "script.py"
        proj.join(f).write("a" * 1000)

        # requirements doesn't exist, so exit=1
        cmd_output("git", "add", f)
        assert main(argv=[f]) == 1

        # requirements does exist, so exit=0
        cmd_output("git", "add", f)
        assert main(argv=[f]) == 0


def test_new_reqs_file_not_added(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx() as proj:
        with pyproj_ctx():
            pass
        # Should not fail since 'requirements-dev.txt' is not added to git yet
        f = "requirements.txt"
        proj.join(f).write("a" * 1000)
        cmd_output("git", "add", f)
        assert main(argv=[f, "--requirements", "requirements-dev.txt"]) == 1
        assert main(argv=[f, "--requirements", "requirements-dev.txt"]) == 0


def test_without_hashes_option(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx() as proj:
        with pyproj_ctx():
            pass
        # Should not fail since 'requirements-dev.txt' is not added to git yet
        f = "requirements.txt"
        proj.join(f).write("a" * 1000)
        cmd_output("git", "add", f)
        print(cmd_output("poetry", "self", "-V"))
        assert (
            main(
                argv=[
                    f,
                    "--requirements",
                    "requirements-dev.txt",
                    "--poetry='--without-hashes'",
                ]
            )
            == 1
        )
        assert (
            main(
                argv=[
                    f,
                    "--requirements",
                    "requirements-dev.txt",
                    "--poetry='--without-hashes'",
                ]
            )
            == 0
        )
