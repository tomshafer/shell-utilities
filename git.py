"""
Return a shell prompt decoration listing the current directory's Git status.
This script is a rough clone of the Haskell implementation of
<https://github.com/olivierverdier/zsh-git-prompt>.

Usage: git.py [-h]
"""

import subprocess
import shlex
import sys

from docopt import docopt


def query_git():
    """
    Query Git for the PWD's status.

    Returns
    -------
    subprocess.CompletedProcess
        a CompletedProcess object containing a return code and STDOUT
    """
    return subprocess.run(
        shlex.split('git status --porcelain=2 --branch'),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)


def collect_response(response_lines):
    """
    Collect a Git response into a dictionary by response type.

    Arguments
    ---------
    response_lines: iterable
        a list of lines of text returned by Git

    Returns
    -------
    dict
        a dictionary with keys corresponding to `git status` output types
        (e.g., '#', '1', or '?') and lists of lines as values
    """
    response_dict = {}
    for entry in filter(None, response_lines):
        prefix = entry[0]
        if prefix in response_dict:
            response_dict[prefix] += [entry]
        else:
            response_dict[prefix] = [entry]
    return response_dict


def parse_branches(branch_list):
    """
    Extract branch meta data from a list of Git response lines.

    Arguments
    ---------
    branch_list: iterable
        list of branch-related entries beginning with the string '# '

    Returns
    -------
    dict
        a dictionary containing branch meta data
    """
    return dict(x.lstrip('# ').split(maxsplit=1) for x in branch_list)


def get_branch(branch_dict, n_hash_chars=7, hash_prefix=':'):
    """
    Extract branch name from banch meta data.
    If no branch name is found, fall back to HEAD's hash.

    Arguments
    ---------
    branch_dict: dict
        branch meta data dictionary
    n_hash_chars: int
        number of characters to print if falling back to a Git hash
    hash_prefix: str
        string to prepend to a hash to diambiguate from a branch name

    Returns
    -------
    dict
        a dictionary containing branch meta data
    """
    if branch_dict['branch.head'].startswith('('):
        return '{:s}{:s}'.format(
            hash_prefix,
            branch_dict['branch.oid'][:n_hash_chars]
        )
    return branch_dict['branch.head']


def parse_modified(full_dict, ignored_keys=('#', '?')):
    """
    Extract 'staged' and 'modified' counts from Git status lines.

    Arguments
    ---------
    full_dict: dict
        full meta data dictionary
    ignored_keys: iterable
        keys that should not contribute towards the staged and modified counts
        (e.g., branch meta data or untracked files)

    Returns
    -------
    list
        a list of two counts: [num_staged, num_modified]
    """
    counts = [0, 0]
    for k in full_dict:
        if k not in ignored_keys:
            values = [x.split()[1].index('.') for x in full_dict[k]]
            for v in values:
                counts[v] += 1
    return counts


def parse_ab(branch_dict):
    """
    Extract 'ahead/behind' counts from Git status lines.

    Arguments
    ---------
    branch_dict: dict
        branch meta data dictionary

    Returns
    -------
    list
        a list of two counts: [num_ahead, num_behind]
    """
    if 'branch.ab' not in branch_dict:
        return [0, 0]
    return [int(x[1:]) for x in branch_dict['branch.ab'].split()]


def parse_git_response(utf8_response):
    """
    Parse a UTF8-encoded Git response string into a list of values.

    Arguments
    ---------
    utf8_response: str
        UTF8-encoded string containing the Git response

    Returns
    -------
    list
        a list of six values corresponding to the Git status:
        [branch_text, n_untracked, n_staged, n_modified, n_ahead, n_behind]
    """
    response_dict = collect_response(utf8_response.strip().split('\n'))

    # Branch-related meta data
    if '#' not in response_dict:
        raise KeyError('git did not return branch information')
    branch_info = parse_branches(response_dict['#'])
    branch = get_branch(branch_info)
    n_ahead, n_behind = parse_ab(branch_info)

    n_untracked = len(response_dict['?']) if '?' in response_dict else 0
    n_modified, n_staged = parse_modified(response_dict)

    return [branch, n_untracked, n_staged, n_modified, n_ahead, n_behind]


if __name__ == '__main__':
    args = docopt(__doc__)
    query = query_git()
    if query.returncode != 0:
        sys.exit(0)

    branch_name, untracked, staged, modified, ahead, behind = \
        parse_git_response(query.stdout.decode('utf8'))

    str_ahead = ('↑%d' % ahead) if ahead else ''
    str_behind = ('↓%d' % behind) if behind else ''

    if untracked + staged + modified == 0:
        str_status = '$fg_bold[green]✓${reset_color}'
    else:
        str_status = '{}{}{}'.format(
            '${fg_bold[magenta]}•%d${reset_color}' % staged if staged else '',
            '${fg_bold[blue]}+%d${reset_color}' % modified if modified else '',
            '...' if untracked else '')

    sys.stdout.write(' ({}{}{}|{})'.format(
        '${fg_bold[magenta]}%s${reset_color}' % branch_name,
        str_ahead, str_behind, str_status))
