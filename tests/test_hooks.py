from poetry_create_pkg_version.hook import main
from poetry_create_pkg_version.utils import cmd_output


def test_adding_nothing(tmpdir):
    with tmpdir.as_cwd():
        # Should not fail with default
        cmd_output("git", "init")
        tmpdir.join("f.py").write("a" * 10000)
        cmd_output("git", "add", "f.py")
        main(argv=["pyproject.toml"]) == 1
