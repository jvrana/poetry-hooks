from poetry_hooks.utils.safe_file_writer import write_safe_file
import ast
import os
import subprocess
from collections import OrderedDict
from itertools import zip_longest
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Set

import toml
from poetry_hooks.utils.safe_file_writer import write_safe_file
from poetry_hooks.__version__ import __version__, __title__


class CalledProcessError(RuntimeError):
    pass


def added_files() -> Set[str]:
    cmd = ("git", "diff", "--staged", "--name-only", "--diff-filter=A")
    return set(cmd_output(*cmd).splitlines())


def cmd_output(*cmd: str, retcode: Optional[int] = 0, **kwargs: Any) -> str:
    kwargs.setdefault("stdout", subprocess.PIPE)
    kwargs.setdefault("stderr", subprocess.PIPE)
    proc = subprocess.Popen(cmd, **kwargs)
    stdout, stderr = proc.communicate()
    stdout = stdout.decode()
    if retcode is not None and proc.returncode != retcode:
        raise CalledProcessError(cmd, retcode, proc.returncode, stdout, stderr)
    return stdout


class DottedDict(dict):
    def get(self, key, default=...):
        if key in self:
            if default is not ...:
                val = super().get(key, default)
            else:
                val = super().get(key)
        else:
            keys = key.split(".")
            if default is not ...:
                def getitem(d, k):
                    return d.get(k, default)

            else:
                def getitem(d, k):
                    return d[k]

            def getter(d, k):
                if k.startswith("[") and k.endswith("]"):
                    vallist = []
                    if not isinstance(d, list) or not isinstance(d, tuple) or not isinstance(d, dict):
                        d = {}
                    for _v in d:
                        val = getitem(_v, k[1:-1])
                        if isinstance(val, dict):
                            val = self.__class__(val)
                        vallist.append(val)
                    return vallist
                else:
                    return getitem(d, k)

            val = getter(dict(self), keys[0])
            for key in keys[1:]:
                val = getter(val, key)
        if isinstance(val, dict):
            val = self.__class__(val)
        return val


def main_dir() -> Path:
    return Path(os.getcwd())


def get_pyproject_toml():
    path = main_dir().joinpath("pyproject.toml")
    try:
        with open(path) as f:
            return DottedDict(toml.load(f))
    except FileNotFoundError:
        msg = "A `pyproject.toml` file is required. Could not find {}".format(path)
        raise FileNotFoundError(msg)


def get_main_pkg():
    project = get_pyproject_toml()
    pkgs = project.get("tool.poetry.packages")
    if pkgs:
        pkgdata = pkgs[0]
        pkg = Path(pkgdata.get('from', '.'))
        pkg = pkg.joinpath(pkgdata['include'])
    else:
        pkg = project.get("tool.poetry.name", None)
    if pkg is None:
        raise RuntimeError("Could not find main package")

    pkg = main_dir().joinpath(pkg)
    if not pkg.is_dir():
        raise NotADirectoryError("Package '{}' does not exist. Please review your pyproject.toml file.".format(pkg))
    return pkg


def get_version():
    project = get_pyproject_toml()
    version = project.get("tool.poetry.version")
    return version


def get__version__path() -> Path:
    return get_main_pkg().joinpath("__version__.py")


def str_compare(s1, s2):
    def replace_quotes(s):
        a, b = '"', "'"
        _s = s.replace(a, b)
        _s = _s.replace(b, a)
        return _s

    return s1 == s2 or s1 == replace_quotes(s2)


def dict_compare(d1, d2):
    items1 = sorted(d1.items())
    items2 = sorted(d2.items())
    same = True
    for a, b in zip_longest(items1, items2):
        if a is None or b is None:
            same = False
        else:
            k1, v1 = a
            k2, v2 = b
            if k1 != k2:
                same = False
            elif isinstance(v1, str) and isinstance(v2, str):
                same = str_compare(v1.strip(), v2.strip())
            else:
                same = v1 == v2
            if not same:
                break
    return same


def create__version__str():
    data = OrderedDict()
    project = get_pyproject_toml()

    data["__version__"] = project.get("tool.poetry.version")
    data["__title__"] = project.get("tool.poetry.name")
    data["__authors__"] = project.get("tool.poetry.authors", [])
    data["__repository__"] = project.get("tool.poetry.repository", "")
    data["__homepage__"] = project.get("tool.poetry.homepage", "")
    data["__description__"] = project.get("tool.poetry.homepage", "")
    data["__maintainers__"] = project.get("tool.poetry.maintainers", "")
    data["__readme__"] = project.get("tool.poetry.readme", "")
    data["__license__"] = project.get("tool.poetry.license", "")

    version_data = {
        "header": [
            "# __version__.py",
            "# autogenerated by {} {}".format(__title__, __version__),
        ],
        "variables": data,
    }

    version_str = ""
    version_str += "\n".join(version_data["header"])
    version_str += "\n\n"
    for k, v in version_data["variables"].items():
        if isinstance(v, str):
            v = "'{}'".format(v)
        version_str += "{k} = {v}\n".format(k=k, v=v)
    version_str += "\n"
    return version_str


def parse__version__str(s):
    lines = s.split("\n")
    lines = map(lambda x: x.strip(), lines)
    lines = filter(lambda x: len(x) > 0 and not x.startswith("#"), lines)

    variables = {}
    for line in lines:
        line = line.split("#")[0]
        if "=" in line:
            k, v = line.split("=")
            v = v.split("#")[0].strip()
            v = ast.literal_eval(v)

            variables[k.strip()] = v
    return variables


def get__version__exists():
    return get__version__path().exists()


def get__version__changed():
    if not get__version__exists():
        old_ver_str = ""
    else:
        with open(get__version__path()) as f:
            old_ver_str = f.read()
    new_ver_str = create__version__str()
    new_ver_data = parse__version__str(new_ver_str)
    old_ver_data = parse__version__str(old_ver_str)
    return not dict_compare(new_ver_data, old_ver_data)


def write__version__():
    return write_safe_file(get__version__path(), create__version__str())
