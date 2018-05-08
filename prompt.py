"""
Generate a customized PWD string for, e.g., an Unix prompt.

Usage: prompt.py [--debug] [--no-tilde] [-n FULL_PATHS] [PATH]

Options:
    -n FULL_PATHS   Number of directories to keep full width [default: 1]

    --debug         Print the raw PATH to stderr
    --no-tilde      Do not compress $HOME to '~'

If PATH is specified, then it is truncated and returned. If PATH is
unspecified, then os.getcwd() is called to find the working directory.
"""

import os
import re
import sys
from docopt import docopt


def truncated_path(path=None, home_tilde=True, n_full=1):
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
    path = args['PATH']
    if path is None:
        path = os.getcwd()

    if args['--debug']:
        sys.stderr.write(path)

    if home_tilde:
        path = re.sub(os.environ['HOME'], '~', path)

    if n_full > 0:
        pieces = path.split('/')
        for i in range(len(pieces)):
            j = len(pieces) - i - 1
            if i >= n_full and pieces[j]:
                pieces[j] = pieces[j][0]

    return '/'.join(pieces)


if __name__ == '__main__':
    args = docopt(__doc__)
    sys.stdout.write(truncated_path(
        home_tilde=not args['--no-tilde'],
        n_full=int(args['-n'])))
