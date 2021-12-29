import re
import subprocess
import sys

STALE_REGEX = re.compile(r'(?:\*?\s+)?([\w/\-.]+)\s+[0-9a-f]+ (?:\[[\w/\-.]+(: gone)?])?.*')


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
            continue  # doesn't match what we are looking for

        if match.group(2) is not None:
            stale_branches.add(match.group(1))

    return stale_branches


def detect_master_branch(remote: str) -> str:
    matcher = re.compile(r'^\s+(\w+)/(\w+)')

    remote_branches = set()

    # attempt to detect
    cmd = ['git', 'branch', '--list', '-r']
    for line in subprocess.check_output(cmd).decode().splitlines():
        match = matcher.search(line)
        assert match is not None

        # split the remote name
        branch_remote, branch_name = match.groups()
        if branch_remote == remote:
            remote_branches.add(branch_name)

    for master_name in ('master', 'main', 'trunk'):
        if master_name in remote_branches:
            return master_name

    raise RuntimeError(f'Unable to detect master branch name: {",".join(list(sorted(remote_branches)))}')
