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
    args = parser.parse_args(argv)
    return args


def run():
    retv = 0
    if get__version__changed():
        write__version__()
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
    exit_code = run()
    return exit_code
