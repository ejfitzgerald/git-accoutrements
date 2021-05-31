#!/usr/bin/env python3
import argparse
import re
import subprocess

from accoutrements import detect_upstream_remote


def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fetch', action='store_true', help='Fetch the lastest updates from the remote')
    return parser.parse_args()


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


def main():
    args = parse_commandline()

    remote = detect_upstream_remote()
    print(f'Upstream remote: {remote}')

    # fetch the latest changes from the remote
    if args.fetch:
        cmd = ['git', 'fetch', remote, '-p']
        subprocess.check_call(cmd)

    # detect the master branch name
    master_name = detect_master_branch(remote)

    # create the new branch
    cmd = ['git', 'checkout', '-B', master_name, f'{remote}/{master_name}']
    subprocess.check_call(cmd)
