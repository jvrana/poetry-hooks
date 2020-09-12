from os.path import abspath, dirname, join
from poetry_hooks.version_up import logger
import pytest
from pathlib import Path
import toml
import functools
from contextlib import contextmanager
from poetry_hooks.utils import cmd_output
from py.path import local as LocalPath
from typing import ContextManager, Tuple, Callable

logger.setLevel("DEBUG")


@pytest.fixture
def fixtures() -> Path:
    here = abspath(dirname(__file__))
    return LocalPath(join(here, 'fixtures'))


@pytest.fixture
def pyproject(fixtures):
    return toml.loads(fixtures.join('fake_pyproject.toml').read_txt())


@contextmanager
def create_project(path: LocalPath, project_name, pkg = None, git: bool = True):
    project = path.join(project_name).mkdir()
    if pkg:
        project.join(pkg).mkdir()
    with project.as_cwd():
        if git:
            cmd_output('git', 'init')
        yield project


@contextmanager
def create_pyproject(template):
    data = toml.loads(template.read())
    yield data
    print("dumping")
    with open('pyproject.toml', 'w') as f:
        toml.dump(data, f)


@pytest.fixture
def new_project(fixtures, tmpdir) -> Tuple[
        Callable[..., ContextManager[LocalPath]],
        Callable[..., ContextManager[dict]]]:
    """
    .. code-block::

        def test_foo(new_project):
            project_context, pyproject_context = new_project
            with project_context(pkg_name=..., git=True) as project:
                with pyproject_context() as pyproject:
                    pyproject['data'] = 1
                # do stuff with new pyproject.toml

    :param fixtures:
    :param tmpdir:
    :return:
    """
    print(Path(tmpdir))
    proj_ctx = functools.partial(create_project, path=tmpdir, project_name='myproject')
    toml_ctx = functools.partial(create_pyproject, template=fixtures.join('fake_pyproject.toml'))
    return proj_ctx, toml_ctx


@pytest.mark.parametrize(
    'git', [True, False]
)
@pytest.mark.parametrize(
    'pkg', ['pkg1', 'pkg2']
)
def test_new_project(new_project, git, pkg):
    project, pyproject = new_project
    with project(pkg=pkg, git=git) as proj:
        with pyproject() as pyproj:
            pyproj['tool']['poetry']['version'] = 'someversionnumber'
        print(proj)
        assert proj.join(pkg).isdir()
        assert proj.join('.git').isdir() == git
        assert proj.join('pyproject.toml').exists()
        assert 'someversionnumber' in proj.join('pyproject.toml').read()
        assert '0.1.1.1.1' not in proj.join('pyproject.toml').read()
