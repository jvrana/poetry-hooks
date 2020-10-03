import argparse
import logging
import os
from typing import Optional
from typing import Sequence

from poetry_hooks.utils import cmd_output


logger = logging.getLogger("poetry_export_hook")


def poetry_cmd(*args):
    return ("poetry", "export", "-f", "requirements.txt") + args


def poetry_export(filename: str, args):
    retv = 0
    out = cmd_output(*poetry_cmd(*args))
    create_new = False
    if not os.path.isfile(filename):
        logger.info("File '{}' does not exist.".format(filename))
        create_new = True
    else:
        a = open(filename).read().strip()
        b = out.strip()
        if not a == b:
            create_new = True
            logger.info("'{f}' and new '{f}' do not match.".format(f=filename))
            # try:
            #     if logger.isEnabledFor("DEBUG"):
            #         result = difflib.unified_diff(
            #             a.split("\n"), b.split("\n"), fromfile=filename, tofile="new"
            #         )
            #         for r in result:
            #             logger.debug(r)
            # except Exception as e:
            #     logger.error(
            #         "There was an error logging difference. exception: {}".format(
            #             str(e)
            #         )
            #     )
    if create_new:
        logger.info("Writing new '{}'".format(filename))
        with open(filename, "w") as f:
            f.write(out)
        logger.debug(out)
        retv = 1
    return retv


PYPROJECT = "pyproject.toml"
POETRYLOCK = "poetry.lock"


def run(filenames, filename, args):
    retv = 0
    files = {PYPROJECT, POETRYLOCK, filename}
    if files.intersection(set(filenames)) or not os.path.isfile(filename):
        retv = poetry_export(filename=filename, args=args)
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
        '-p',
        '--poetry',
        help='Poetry arguments (as a str)',
        default=''
    )
    args = parser.parse_args(argv)

    poetry_args = args.poetry.strip('"').strip("'")
    poetry_args = [a.strip() for a in poetry_args.split(' ') if a.strip()]
    args.poetry = poetry_args
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

    return run(args.filenames, filename=args.requirements, args=args.poetry)


if __name__ == "__main__":
    exit(main())
