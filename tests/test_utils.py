from pathlib import Path

import pytest
from poetry_hooks.utils import create__version__str
from poetry_hooks.utils import get_main_pkg
from poetry_hooks.utils import get_pyproject_toml
from poetry_hooks.utils import get_version
from poetry_hooks.utils import parse__version__str


@pytest.fixture
def fake_project(tmpdir, fixtures):
    myproject = tmpdir.join("myproject").mkdir()
    myproject.join("test_pkg").mkdir()
    fixtures = Path(fixtures)
    with myproject.as_cwd():
        txt = fixtures.joinpath("fake_pyproject.toml").read_text()
        myproject.join("pyproject.toml").write(txt)
    return myproject


def test_get_pyproject_toml(fake_project):
    with fake_project.as_cwd():
        pyproject = get_pyproject_toml()
        print(pyproject)


def test_get_main_pkg(fake_project):
    with fake_project.as_cwd():
        print(get_pyproject_toml())
        pkg = get_main_pkg()
        print(pkg)


def test_get_version(fake_project):
    with fake_project.as_cwd():
        print(get_version())


def test_create_version_str(fake_project):
    with fake_project.as_cwd():
        print(create__version__str())


def test_parse_version_str(fake_project):
    with fake_project.as_cwd():
        print(create__version__str())
        data = parse__version__str(create__version__str())
        print(data)
