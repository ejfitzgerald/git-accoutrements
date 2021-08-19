import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional, Tuple

import toml

TARGET_FILENAME = '.git-ditto.toml'
HEADER = r"""
________  .__  __    __          
\______ \ |__|/  |__/  |_  ____  
 |    |  \|  \   __\   __\/  _ \ 
 |    `   \  ||  |  |  | (  <_> )
/_______  /__||__|  |__|  \____/ 
        \/                       

"""

SCAN_DIR_EXCEPTIONS = {
    'node_modules',
}


@dataclass
class DittoConfig:
    name: Optional[str] = None
    email: Optional[str] = None
    signing_key: Optional[str] = None

    @property
    def updates_present(self) -> bool:
        return any([
            self.name is not None,
            self.email is not None,
            self.signing_key is not None,
        ])


def find_ditto_config() -> Optional[str]:
    current_folder = os.path.abspath(os.getcwd())

    while True:
        ditto_path = os.path.join(current_folder, TARGET_FILENAME)
        if os.path.exists(ditto_path):
            return ditto_path

        next_folder = os.path.dirname(current_folder)
        if next_folder == '/':
            break

        current_folder = next_folder


def load_ditto_config() -> DittoConfig:
    ditto_cfg_path = find_ditto_config()
    cfg = DittoConfig()
    if ditto_cfg_path is not None:
        with open(ditto_cfg_path, 'r') as cfg_file:
            ditto_cfg = toml.load(cfg_file)

        user_data = ditto_cfg.get('user', {})
        cfg.name = user_data.get('name')
        cfg.email = user_data.get('email')
        cfg.signing_key = user_data.get('signingkey')

    return cfg


def clone_url(text) -> Tuple[str, str]:
    if text in ('scan', 'update'):
        return text, '.'

    match = re.match(r'.*?/(.*)\.git$', text)
    if match is None:
        print('Unable to parse the clone url')
        sys.exit(1)

    return text, match.group(1)


def parse_commandline() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=clone_url, help='The URL to make the clone')
    parser.add_argument('--deep', action='store_true', help='Scan deeply')
    return parser.parse_args()


def _filter_folder(root: str, path: str):
    full_path = os.path.join(root, path)

    if not os.path.isdir(full_path):
        return False

    if path in SCAN_DIR_EXCEPTIONS:
        return False

    if path.startswith('.'):
        return False

    return True


def _run_scan(args: argparse.Namespace, path: str):
    scan_list = [path]
    while len(scan_list) > 0:
        current = scan_list.pop(0)

        git_path = os.path.join(current, '.git')

        # check to see if the current level is a git repo
        if os.path.isdir(git_path):
            yield current

            # check to see if this git repo has git modules
            has_git_modules = os.path.exists(os.path.join(current, '.gitmodules'))

            # Determine if we should stop processing this branch. In the answer to this should be yes since we have
            # found a git repo. However, if there are git modules then we should continue the search down. Alternatively
            # if the user has specified the deep flag we continue searching
            if has_git_modules or args.deep:
                skip_current_level = False
            else:
                skip_current_level = True

            # skip the level if we desire
            if skip_current_level:
                continue

        # update the scan list
        scan_list.extend(
            map(
                lambda x: os.path.join(current, x),  # add the current prefix
                filter(
                    lambda x: _filter_folder(current, x),
                    os.listdir(current)
                )
            )
        )


def run_scan(args: argparse.Namespace, cfg: DittoConfig, search_folder: str):
    print('Run scan')

    for git_repo_path in _run_scan(args, search_folder):
        # print(git_repo_path)
        run_update(cfg, git_repo_path)


def run_update(cfg: DittoConfig, destination_folder: str):
    assert os.path.isdir(os.path.join(destination_folder, '.git'))

    # print some user headers
    if cfg.updates_present:
        print()
        print(f"Configuration updates ({destination_folder})")
        print()

    # apply the configuration to the clone
    if cfg.name is not None:
        cmd = ['git', 'config', 'user.name', cfg.name]
        subprocess.check_call(cmd, cwd=destination_folder)
        print(f'Set user name to: {cfg.name}')

    if cfg.email is not None:
        cmd = ['git', 'config', 'user.email', cfg.email]
        subprocess.check_call(cmd, cwd=destination_folder)
        print(f'Set user email to: {cfg.email}')

    if cfg.signing_key is not None:
        cmd = ['git', 'config', 'user.signingkey', cfg.signing_key]
        subprocess.check_call(cmd, cwd=destination_folder)
        print(f'Set user signing key to: {cfg.signing_key}')


def main():
    args = parse_commandline()
    cfg = load_ditto_config()

    url, destination_folder = args.url

    if url == 'update':
        run_update(cfg, destination_folder)
        return
    elif url == 'scan':
        run_scan(args, cfg, destination_folder)
        return

    # print a nice user header
    print(HEADER)

    # clone the folder
    cmd = ['git', 'clone', url]
    subprocess.check_call(cmd)

    run_update(cfg, destination_folder)
