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
        print(ditto_cfg)

        user_data = ditto_cfg.get('user', {})
        cfg.name = user_data.get('name')
        cfg.email = user_data.get('email')
        cfg.signing_key = user_data.get('signingkey')

    return cfg


def clone_url(text) -> Tuple[str, str]:
    match = re.match(r'.*?/(.*)\.git$', text)
    if match is None:
        print('Unable to parse the clone url')
        sys.exit(1)

    return text, match.group(1)


def parse_commandline() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=clone_url, help='The URL to make the clone')
    return parser.parse_args()


def main():
    args = parse_commandline()
    cfg = load_ditto_config()

    url, destination_folder = args.url

    # print a nice user header
    print(HEADER)

    # clone the folder
    cmd = ['git', 'clone', url]
    subprocess.check_call(cmd)

    # print some user headers
    if cfg.updates_present:
        print()
        print("Configuration updates")
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
