# coding: utf-8

import argparse as ap
import os
import re
import sys


def parse_args():
    """Provide a dependency-free command-line interface."""
    p = ap.ArgumentParser(
        description="Generate a customized PWD string for a Unix prompt.",
        epilog=(
            "If PATH is specified, then it is truncated and returned. "
            "If PATH is unspecified, then os.getcwd() is called to find "
            "the working directory."
        ),
    )
    p.add_argument(
        "-n",
        metavar="FULL_PATHS",
        type=int,
        default=1,
        help="Number of directories to keep full width",
    )
    p.add_argument(
        "--debug",
        dest="DEBUG",
        action="store_true",
        help="Print the raw PATH to stderr",
    )
    p.add_argument(
        "--no-tilde",
        dest="NO_TILDE",
        action="store_true",
        help="Do not compress $HOME to '~'",
    )
    p.add_argument("PATH", type=str, nargs="?", default=os.getcwd())
    return p.parse_args()


def truncated_path(path=None, home_tilde=True, n_full=1, debug=False):
    """
    Return the PWD string, optionally with the user's home directory truncated
    to a tilde and/or a number of subdirectory names truncated.

    Parameters
    ----------
    path: string or None
        if None, use os.getcwd()
    home_tilde: boolean
        whether to compress $HOME to '~'
    n_full: int
        number of not-compressed directories, beginning from the PWD

    Returns
    -------
    string
        the reconstructed path
    """
    if path is None:
        path = os.getcwd()
    if debug:
        sys.stderr.write(path)
    if home_tilde:
        path = re.sub(os.environ["HOME"], "~", path)
    if n_full > 0:
        pieces = path.split("/")
        for i in range(len(pieces)):
            j = len(pieces) - i - 1
            if i >= n_full and pieces[j]:
                pieces[j] = pieces[j][0]
    return "/".join(pieces)


if __name__ == "__main__":
    args = parse_args()
    sys.stdout.write(
        truncated_path(
            home_tilde=not args.NO_TILDE,
            n_full=args.n,
            debug=args.DEBUG
        )
    )
