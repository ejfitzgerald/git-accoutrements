#!/usr/bin/env python3
import argparse
import subprocess

from accoutrements import detect_upstream_remote


def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='The name of the branch')
    parser.add_argument('-p', '--push', action='store_true', help='Push the new branch so that it is setup to track')
    return parser.parse_args()


def main():
    args = parse_commandline()

    remote = detect_upstream_remote()
    print(f'Upstream remote: {remote}')

    # fetch the latest changes from the remote
    cmd = ['git', 'fetch', remote, '-p']
    subprocess.check_call(cmd)

    # create the new branch
    branch_name = f'feature/{args.name}'
    cmd = ['git', 'checkout', '-b', branch_name]
    subprocess.check_call(cmd)

    # reset the feature branch on top of the remote upstream
    cmd = ['git', 'reset', '--hard', f'{remote}/master']
    subprocess.check_call(cmd)

    # push if required
    if args.push:
        cmd = ['git', 'push', '-u', 'origin', branch_name]
        subprocess.check_call(cmd)
