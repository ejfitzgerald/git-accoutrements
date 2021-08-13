#!/usr/bin/env python3
import argparse
import re
import subprocess

from accoutrements import detect_upstream_remote, detect_master_branch


def parse_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fetch', action='store_true', help='Fetch the lastest updates from the remote')
    return parser.parse_args()


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
