import argparse
import difflib
import logging
import os
from typing import Optional
from typing import Sequence
from typing import Tuple

from poetry_hooks.utils import cmd_output


logger = logging.getLogger("poetry_export_hook")


def poetry_cmd(filename: str, dev: bool = False, extras: Tuple[str] = ()):
    cmd = ["poetry", "export", "-f", "requirements.txt"]
    if dev:
        cmd += ["--dev"]
    if extras:
        for e in extras:
            cmd += ["-E", e]
    return cmd


def poetry_export(filename: str, dev: bool = False, extras: Tuple[str] = ()):
    retv = 0
    out = cmd_output(*poetry_cmd(filename, dev, extras))
    create_new = False
    if not os.path.isfile(filename):
        logger.info("File '{}' does not exist.".format(filename))
        create_new = True
    else:
        a = open(filename).read().strip()
        b = out.strip()
        if not a == b:
            try:
                logger.info("'{f}' and new '{f}' do not match.".format(f=filename))
                create_new = True
                if logger.isEnabledFor("DEBUG"):
                    result = difflib.unified_diff(
                        a.split("\n"), b.split("\n"), fromfile=filename, tofile="new"
                    )
                    for r in result:
                        logger.debug(r)
            except Exception as e:
                logger.error(
                    "There was an error logging difference. exception: {}".format(
                        str(e)
                    )
                )
    if create_new:
        logger.info("Writing new '{}'".format(filename))
        with open(filename, "w") as f:
            f.write(out)
        logger.debug(out)
        retv = 1
    return retv


PYPROJECT = "pyproject.toml"
POETRYLOCK = "poetry.lock"


def run(filenames, filename, dev, extras):
    retv = 0
    files = {PYPROJECT, POETRYLOCK, filename}
    if files.intersection(set(filenames)) or not os.path.isfile(filename):
        retv = poetry_export(filename=filename, dev=dev, extras=tuple(extras))
    else:
        logger.warning(
            "Filename '{}' not in expected filenames {}".format(filename, filenames)
        )
    return retv


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.",
        default=[],
    )
    parser.add_argument(
        "--requirements",
        help="Filename of the requirements file.",
        default="requirements.txt",
    )
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Verbosity (-v, -vv, -vvv)"
    )
    parser.add_argument(
        "-E",
        "--extras",
        action="append",
        help='Export extras ("-E docs -E lint" etc.)',
        default=[],
    )
    parser.add_argument(
        "-D",
        "--dev",
        action="store_true",
        default=False,
        help="Export development requirements",
    )
    args = parser.parse_args(argv)
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    logger.debug("main: argv: {}".format(argv))
    args = parse_args(argv)
    if args.verbose == 3:
        logger.setLevel("DEBUG")
    elif args.verbose == 2:
        logger.setLevel("INFO")
    elif args.verbose == 1:
        logger.setLevel("WARNING")

    logger.debug("Args: {}".format(args))
    return run(
        args.filenames, filename=args.requirements, dev=args.dev, extras=args.extras
    )


if __name__ == "__main__":
    exit(main())
