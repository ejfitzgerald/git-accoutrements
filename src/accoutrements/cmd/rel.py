import argparse
import subprocess
from typing import Optional

from accoutrements import detect_upstream_remote
from accoutrements.config import has_signing_key
from accoutrements.versions import next_version, VALID_MODES


def current_version(cwd: Optional[str] = None) -> str:
    cmd = ['git', 'describe', '--always']
    output = subprocess.check_output(cmd, cwd=cwd).decode().strip()
    return output


def create_tag(name: str, dry_run: bool = False, cwd: Optional[str] = None):
    sign_type = '-s' if has_signing_key(cwd=cwd) else '-a'

    # create the git tag
    if not dry_run:
        cmd = [
            'git',
            'tag',
            sign_type,
            name,
            '-m', name,
        ]
        subprocess.check_call(cmd, cwd=cwd)

    else:
        print('DRY-RUN: Tag Version:', name)


def push_tag(remote: str, name: str, dry_run: bool = False, cwd: Optional[str] = None):
    if not dry_run:
        cmd = [
            'git',
            'push',
            remote,
            name,
        ]
        subprocess.check_call(cmd, cwd=cwd)

    else:
        print('DRY-RUN: Push Tag Version:', name)


def determine_next_version(current_ver: str, tag: str) -> str:
    if tag in VALID_MODES:
        return next_version(current_ver, tag)
    return tag


def parse_commandline() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('tag', nargs='?', default='patch',
                        help=f'The name of the tag or one of the auto modes. Modes: {",".join(VALID_MODES)}')
    parser.add_argument('-n', '--no-push', action='store_true', help='Disable pushing of the tag')
    parser.add_argument('--dry-run', action='store_true', help='Disable the going actual operations for testing')
    parser.add_argument('-w', '--working-dir', help='The working directory to be used')
    return parser.parse_args()


def main():
    args = parse_commandline()
    cwd = args.working_dir

    current_ver = current_version()
    next_ver = determine_next_version(current_ver, args.tag)
    remote = detect_upstream_remote()

    print(f'Current Version: {current_ver}')
    print(f'Next Version...: {next_ver}')
    print(f'Upstream remote: {remote}')
    if cwd is not None:
        print(f'Working Dir....: {cwd}')
    if args.dry_run:
        print('Dry Run........: Yes')
    if args.no_push:
        print('No Push........: Yes')
    print()
    input('Press enter to continue')
    print()

    # create the tag
    create_tag(next_ver, dry_run=args.dry_run, cwd=cwd)

    # push the tag
    if not args.no_push:
        push_tag(remote, next_ver, dry_run=args.dry_run, cwd=cwd)
