import re
import subprocess
import sys

STALE_REGEX = re.compile(r'(?:\*?\s+)?([\w/-]+)\s+[0-9a-f]+ (?:\[[\w/-]+(: gone)?\])?.*')


def detect_upstream_remote():
    remotes = subprocess.check_output(['git', 'remote']).decode()
    remotes = set([r.strip() for r in remotes.splitlines()])

    if 'upstream' in remotes:
        return 'upstream'
    elif 'origin' in remotes:
        return 'origin'

    print('Unable to determine the correct upstream remote')
    sys.exit(1)


def detect_stale_branches():
    # get the list of local branches with extra verboseness
    cmd = ['git', 'branch', '-vv']
    output = subprocess.check_output(cmd).decode().strip()

    stale_branches = set()
    for line in output.splitlines():
        line = line.strip()
        match = STALE_REGEX.match(line)

        if match is None:
            print('Match failure: "{}"'.format(line))
            sys.exit(1)

        if match.group(2) is not None:
            stale_branches.add(match.group(1))

    return stale_branches
