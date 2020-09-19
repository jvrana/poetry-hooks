import argparse
import logging
from typing import Optional
from typing import Sequence

from poetry_hooks.utils import get__version__changed
from poetry_hooks.utils import write__version__


logger = logging.getLogger(__name__)


def parse_args(argv):
    logger.debug("arguments: {}".format(argv))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Verbosity (-v, -vv, -vvv)"
    )
    parser.add_argument(
        "-f",
        "--filename",
        default=None,
        help="Filename of the version file (defaults to <pkg>/_version.py)",
    )
    args = parser.parse_args(argv)
    return args


def run(filename: Optional[str] = None):
    retv = 0
    if get__version__changed(filename):
        write__version__(filename)
        retv = 1
    return retv


def main(argv: Optional[Sequence[str]] = None) -> int:
    if argv is None:
        argv = []
    logger.debug("main: argv: {}".format(argv))
    args = parse_args(argv)
    if args.verbose == 3:
        logger.setLevel("DEBUG")
    elif args.verbose == 2:
        logger.setLevel("INFO")
    elif args.verbose == 1:
        logger.setLevel("WARNING")

    logger.debug("Args: {}".format(args))
    exit_code = run(args.filename)
    return exit_code


if __name__ == "__main__":
    exit(main())
