#!/usr/bin/env python3
import argparse
import subprocess

from accoutrements import detect_upstream_remote, detect_stale_branches


def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fetch', action='store_true', help='Fetch the lastest updates from the remote')
    return parser.parse_args()


def main():
    args = parse_commandline()

    # fetch and prune if required
    if args.fetch:
        cmd = ['git', 'fetch', '--prune', '--all']
        subprocess.check_call(cmd)

    remote = detect_upstream_remote()
    print(f'Upstream remote: {remote}')

    # detect all the local branches that exist but no longer have an
    # upstream reference
    stale_branches = detect_stale_branches()
    current_branch = subprocess.check_output(['git', 'branch', '--show-current']).decode().strip()

    print('The following branches will be removed:')
    for branch in sorted(stale_branches):
        print('- {}'.format(branch))
    print()
    if current_branch in stale_branches:
        print(f'Since you are currently on `{current_branch}` you will be checkedout to the upstream master')
        print()
    input('Press enter to continue...')

    # if needed checkout master if we are on this stale branch
    if current_branch in stale_branches:
        cmd = ['git', 'checkout', '-B', 'master', f'{remote}/master']
        subprocess.check_call(cmd)

    # delete the branches
    for branch in stale_branches:
        cmd = ['git', 'branch', '-D', branch]
        subprocess.check_call(cmd)
