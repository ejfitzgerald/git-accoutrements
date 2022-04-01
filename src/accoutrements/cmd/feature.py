#!/usr/bin/env python3
import argparse
import os
import subprocess

from accoutrements import detect_upstream_remote, detect_master_branch, detect_develop_branch


def parse_commandline() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('name', nargs='+', help='The name of the branch')
    parser.add_argument('-p', '--push', action='store_true', help='Push the new branch so that it is setup to track')
    return parser.parse_args()


def create_new_branch(prefix: str, args: argparse.Namespace):
    remote = detect_upstream_remote()
    print(f'Upstream remote: {remote}')

    # fetch the latest changes from the remote
    cmd = ['git', 'fetch', remote, '-p']
    subprocess.check_call(cmd)

    # create the new branch
    base_name = '-'.join(args.name)
    branch_name = f'{prefix}/{base_name}'
    cmd = ['git', 'checkout', '-b', branch_name]
    subprocess.check_call(cmd)

    # check to see if there are any working changse
    cmd = ['git', 'diff', '--exit-code']
    with open(os.devnull, 'w') as null_file:
        exit_code = subprocess.call(cmd, stdout=null_file, stderr=subprocess.STDOUT)
        if exit_code != 0:
            print('Working changes detected, not resetting branch ref')
            return

    # detect the master (and optionally develop) branches that is used with this project
    master_branch_name = detect_master_branch(remote)
    develop_branch_name = detect_develop_branch(remote)

    # prefer the "develop" target branch name over the "master" branch name
    target_branch_name = develop_branch_name or master_branch_name

    # reset the feature branch on top of the remote upstream
    cmd = ['git', 'reset', '--hard', f'{remote}/{target_branch_name}']
    subprocess.check_call(cmd)

    # push if required
    if args.push:
        cmd = ['git', 'push', '-u', 'origin', branch_name]
        subprocess.check_call(cmd)


def main():
    args = parse_commandline()
    create_new_branch('feature', args)
