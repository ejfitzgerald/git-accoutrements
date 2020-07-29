import argparse
import subprocess
from ..colours import yellow, blue
from typing import Optional, Tuple, Set


def parse_commandline() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('branches', nargs='+', help='The branch references that need to be removed')
    parser.add_argument('--dry-run', action='store_true', help='Do not actually delete the branches')
    return parser.parse_args()


def get_remotes() -> Set[str]:
    return set(subprocess.check_output(['git', 'remote']).decode().splitlines())


def extract(remotes: Set[str], ref: str) -> Tuple[Optional[str], str]:
    tokens = ref.split('/')
    if len(tokens) > 2 and tokens[0] == 'remotes' and tokens[1] in remotes:
        branch = '/'.join(tokens[2:])
        remote = tokens[1]
    elif len(tokens) > 1 and tokens[0] in remotes:
        branch = '/'.join(tokens[1:])
        remote = tokens[0]
    else:
        branch = ref
        remote = None

    return remote, branch


def main():
    args = parse_commandline()
    remotes = get_remotes()

    # step 1. collect up all the references and remove all duplicates
    playlist = {}
    for ref in args.branches:
        remote, branch = extract(remotes, ref)

        # add the branch to the playlist
        branches = playlist.get(remote, set())
        branches.add(branch)
        playlist[remote] = branches

    # step 2. display the list for the user
    local_branches = playlist.get(None, [])
    if len(local_branches) > 0:
        print('The following {} branches will be deleted:'.format(yellow('local')))
        for branch in local_branches:
            print('- {}'.format(branch))
    print()

    remotes = list(sorted(filter(lambda x: x is not None, playlist.keys())))
    for remote in remotes:
        remote_branches = list(sorted(playlist[remote]))
        if len(remote_branches) > 0:
            print('The following branches will be deleted from {}:'.format(yellow(remote)))
            for branch in remote_branches:
                print('- {}'.format(branch))
        print()

    # we are dry running then stop here
    if args.dry_run:
        return

    input('Press enter to continue')

    # delete all the local branches
    for branch in local_branches:
        subprocess.check_call(['git', 'branch', '-D', branch])

    # delete all the remote branches
    for remote in remotes:
        remote_branches = list(sorted(playlist[remote]))
        subprocess.check_call(['git', 'push', '--delete', remote] + remote_branches)
