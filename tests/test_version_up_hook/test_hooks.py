import pytest
from poetry_hooks.version_up import main
from poetry_hooks.version_up import parse_args


class TestParseArgs:
    def test_parse_args_default(self):
        args = parse_args(argv=[])
        args.verbose == 0

    def test_parse_args_v(self):
        args = parse_args(argv=["-v"])
        assert args.verbose == 1

    def test_parse_args_vv(self):
        args = parse_args(argv=["-vv"])
        assert args.verbose == 2

    def test_parse_args_vvv(self):
        args = parse_args(argv=["-vvv"])
        assert args.verbose == 3


def test_no_pyroject_toml(new_project):
    proj_ctx, _ = new_project
    with proj_ctx():
        with pytest.raises(FileNotFoundError):
            main() == 1


def test_no_pkg_dir(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx():
        with pyproj_ctx() as pyproj:
            pyproj["tool"]["poetry"]["name"] = "mypkg"
        with pytest.raises(NotADirectoryError):
            main() == 1


def test_basic_project_no_version(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx(pkg="mypkg") as proj:
        with pyproj_ctx() as pyproj:
            pyproj["tool"]["poetry"]["name"] = "mypkg"
        assert not proj.join("mypkg").join("_version.py").exists()
        assert main() == 1
        assert proj.join("mypkg").join("_version.py").exists()


def test_basic_project_version_change(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx(pkg="mypkg") as proj:
        with pyproj_ctx() as pyproj:
            pyproj["tool"]["poetry"]["name"] = "mypkg"
        assert not proj.join("mypkg").join("_version.py").exists()
        assert main() == 1
        assert proj.join("mypkg").join("_version.py").exists()
        assert main() == 0
        assert main() == 0


def test_change_version_name(new_project):
    proj_ctx, pyproj_ctx = new_project
    with proj_ctx(pkg="mypkg") as proj:
        with pyproj_ctx() as pyproj:
            pyproj["tool"]["poetryhooks"] = {"version_up_name": "__version.py"}
            pyproj["tool"]["poetry"]["name"] = "mypkg"
        assert not proj.join("mypkg").join("_version.py").exists()
        assert not proj.join("mypkg").join("__version.py").exists()
        assert main() == 1
        assert proj.join("mypkg").join("__version.py").exists()
        assert not proj.join("mypkg").join("_version.py").exists()
        assert main() == 0
        assert main() == 0
